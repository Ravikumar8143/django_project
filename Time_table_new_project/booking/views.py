from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from slots.models import Room
from .models import RoomBookingRequest


class BookingPage(LoginRequiredMixin, TemplateView):
    """Renders one of the pre-built bookings/*.html templates."""


# Standard teaching-day schedule (matches the grid already assumed elsewhere,
# e.g. dashboard/timetable.html and dashboard/student.html). There's no
# TimeSlot model yet, so this is a fixed fixture rather than DB-driven periods.
STANDARD_SLOTS = [
    {'n': 1, 'start': '08:00', 'end': '08:50', 'label': '08:00-08:50'},
    {'n': 2, 'start': '09:00', 'end': '09:50', 'label': '09:00-09:50'},
    {'n': 3, 'start': '10:00', 'end': '10:50', 'label': '10:00-10:50'},
    {'n': 4, 'start': '11:00', 'end': '11:50', 'label': '11:00-11:50'},
    {'n': 5, 'start': '12:00', 'end': '12:50', 'label': '12:00-12:50'},
    {'n': 7, 'start': '14:00', 'end': '14:50', 'label': '14:00-14:50'},
    {'n': 8, 'start': '15:00', 'end': '15:50', 'label': '15:00-15:50'},
    {'n': 9, 'start': '16:00', 'end': '16:50', 'label': '16:00-16:50'},
]


@login_required
def availability_view(request):
    """JSON API backing the New Booking wizard's live availability grid
    (templates/bookings/create.html calls this via fetch()).

    GET params: date='YYYY-MM-DD' (required for real slot data), slots=comma,
    separated,slot,numbers (only affects which slots the caller is asking
    about -- the response shape is the same either way).

    Room 'status' here is honest, not simulated: RoomBookingRequest doesn't
    track which room or which slot numbers a booking covers (it only has a
    free-text assigned_room field and a single date) -- real per-slot
    conflict detection would need that model extended with a Room FK and a
    slot-numbers field. Until then, a room shows 'booked' only when its
    room_id string happens to appear inside an existing PENDING/APPROVED
    booking's assigned_room text for that date -- a best-effort heuristic.
    """
    date_str = request.GET.get('date', '')
    rooms_qs = Room.objects.select_related('building').filter(is_available=True)

    booked_room_ids = set()
    if date_str:
        same_day_bookings = RoomBookingRequest.objects.filter(
            booking_date=date_str,
            status__in=[RoomBookingRequest.Status.PENDING, RoomBookingRequest.Status.APPROVED],
        ).exclude(assigned_room='')
        for room in rooms_qs:
            if room.room_id and same_day_bookings.filter(assigned_room__icontains=room.room_id).exists():
                booked_room_ids.add(room.pk)

    rooms = [
        {
            'pk': r.pk,
            'room_id': r.room_id,
            'building': r.building.name,
            'building_code': r.building.code,
            'floor': r.floor or '-',
            'room_type': r.room_type,
            'capacity': r.seating_capacity,
            'status': 'booked' if r.pk in booked_room_ids else 'available',
        }
        for r in rooms_qs
    ]

    return JsonResponse({
        'slots_for_day': STANDARD_SLOTS if date_str else [],
        'rooms': rooms,
    })


@login_required
def create_view(request):
    """The 4-step 'New Booking' wizard (templates/bookings/create.html).

    Only booking_date, purpose, and preferred_room map to real fields on
    RoomBookingRequest today. required_room_type, required_capacity,
    purpose_description, is_cross_department, is_recurring, and
    recurrence_end_date are collected by the wizard's UI but NOT persisted --
    RoomBookingRequest has no columns for them yet. Extend that model first
    if those need to be saved.
    """
    if request.method == 'POST':
        booking_date = request.POST.get('booking_date', '').strip()
        purpose = request.POST.get('purpose', '')
        preferred_room_pk = request.POST.get('preferred_room', '')

        assigned_room = ''
        if preferred_room_pk:
            room = Room.objects.filter(pk=preferred_room_pk).first()
            if room:
                assigned_room = f'{room.room_id} ({room.get_room_type_display()}, cap={room.seating_capacity})'

        if booking_date and purpose in dict(RoomBookingRequest.Purpose.choices):
            RoomBookingRequest.objects.create(
                requested_by=request.user,
                booking_date=booking_date,
                purpose=purpose,
                assigned_room=assigned_room,
                status=RoomBookingRequest.Status.PENDING,
            )
            messages.success(request, 'Booking request submitted. Awaiting approval.')
            return redirect('bookings:list')

        messages.error(request, 'Could not submit booking request -- missing date or purpose.')

    return render(request, 'bookings/create.html', {
        'purposes': RoomBookingRequest.Purpose.choices,
        'room_types': list(Room.RoomType),
    })

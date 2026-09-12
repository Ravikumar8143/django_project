from .models import Booking


def pending_bookings_count(request):
    user = getattr(request, 'user', None)
    if user and user.is_authenticated and getattr(user, 'role', None) in ('admin', 'hoi', 'hod'):
        return {'pending_bookings_count': Booking.objects.filter(status='PENDING').count()}
    return {'pending_bookings_count': 0}

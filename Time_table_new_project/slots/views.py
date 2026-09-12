from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST


# Every entry in dashboard/admin.html's "Management Panel" grid, and every
# link in templates/manage/layout.html's sidebar, points at one of these
# section slugs. Sections with a real model behind them get real rows and a
# real "Add New" page; everything else has no model yet, so it renders the
# same manage/list.html page with an empty table ("No records found")
# instead of crashing or dead-ending on a placeholder.
MANAGE_SECTIONS = {
    'users': 'Users',
    'universities': 'Universities',
    'campuses': 'Campuses',
    'buildings': 'Buildings',
    'rooms': 'Rooms',
    'departments': 'Departments',
    'academic_years': 'Academic Years',
    'programs': 'Programs',
    'course_categories': 'Course Categories',
    'courses': 'Courses',
    'offerings': 'Semester Offerings',
    'sections': 'Sections',
    'timeslots': 'Time Slots',
    'timetables': 'Timetables',
    'employee_timetable_list': 'Employee Timetable',
    'bookings': 'Room Bookings',
}

# Singular label used in the "Add <X>" page title.
ADD_LABELS = {
    'users': 'User',
    'bookings': 'Room Booking',
    'universities': 'University',
    'campuses': 'Campus',
    'buildings': 'Building',
    'rooms': 'Room',
}

DEFAULT_HEADERS = {
    'departments': ['Name', 'Code', 'Campus'],
    'academic_years': ['Label', 'Start', 'End'],
    'programs': ['Name', 'Code', 'Department'],
    'course_categories': ['Name'],
    'courses': ['Code', 'Title', 'Category'],
    'offerings': ['Program', 'Semester', 'Academic Year'],
    'sections': ['Name', 'Offering', 'Enrolled'],
    'timeslots': ['Day', 'Slot #', 'Start', 'End'],
    'timetables': ['Academic Year', 'Version', 'Status'],
    'employee_timetable_list': ['Employee', 'Course', 'Room', 'Day'],
}


def _users_rows():
    from user_management.models import User

    headers = ['Username', 'Email', 'Emp ID', 'Department', 'Active']
    rows = [
        {
            'pk': u.pk,
            'cells': [u.username, u.email, u.emp_id or '-', u.dept_code or '-', 'Yes' if u.is_active else 'No'],
            'edit_url': reverse('dashboard:manage_users_edit', args=[u.pk]),
            'delete_url': reverse('dashboard:manage_users_delete', args=[u.pk]),
        }
        for u in User.objects.all().order_by('username')
    ]
    return headers, rows


def _bookings_rows():
    from booking.models import RoomBookingRequest

    headers = ['Requestor', 'Date', 'Purpose', 'Room', 'Status']
    rows = [
        {
            'pk': b.pk,
            'cells': [
                b.requested_by.get_full_name() or b.requested_by.username,
                b.booking_date,
                b.get_purpose_display(),
                b.assigned_room or '-',
                b.get_status_display(),
            ],
            'edit_url': reverse('dashboard:manage_bookings_edit', args=[b.pk]),
            'delete_url': reverse('dashboard:manage_bookings_delete', args=[b.pk]),
        }
        for b in RoomBookingRequest.objects.select_related('requested_by').order_by('-submitted_at')
    ]
    return headers, rows


def _universities_rows():
    from .models import University

    headers = ['Name', 'Code']
    rows = [
        {
            'pk': u.pk,
            'cells': [u.name, u.code],
            'edit_url': reverse('dashboard:manage_universities_edit', args=[u.pk]),
            'delete_url': reverse('dashboard:manage_universities_delete', args=[u.pk]),
        }
        for u in University.objects.all()
    ]
    return headers, rows


def _campuses_rows():
    from .models import Campus

    headers = ['Name', 'University', 'Code']
    rows = [
        {
            'pk': c.pk,
            'cells': [c.name, c.university.name, c.code],
            'edit_url': reverse('dashboard:manage_campuses_edit', args=[c.pk]),
            'delete_url': reverse('dashboard:manage_campuses_delete', args=[c.pk]),
        }
        for c in Campus.objects.select_related('university').all()
    ]
    return headers, rows


def _buildings_rows():
    from .models import Building

    headers = ['Name', 'Campus', 'Code']
    rows = [
        {
            'pk': b.pk,
            'cells': [b.name, b.campus.name, b.code],
            'edit_url': reverse('dashboard:manage_buildings_edit', args=[b.pk]),
            'delete_url': reverse('dashboard:manage_buildings_delete', args=[b.pk]),
        }
        for b in Building.objects.select_related('campus').all()
    ]
    return headers, rows


def _rooms_rows():
    from .models import Room

    headers = ['Room ID', 'Type', 'Building', 'Capacity']
    rows = [
        {
            'pk': r.pk,
            'cells': [r.room_id, r.get_room_type_display(), r.building.name, r.seating_capacity],
            'edit_url': reverse('dashboard:manage_rooms_edit', args=[r.pk]),
            'delete_url': reverse('dashboard:manage_rooms_delete', args=[r.pk]),
        }
        for r in Room.objects.select_related('building').all()
    ]
    return headers, rows


ROWS_FUNCTIONS = {
    'users': _users_rows,
    'bookings': _bookings_rows,
    'universities': _universities_rows,
    'campuses': _campuses_rows,
    'buildings': _buildings_rows,
    'rooms': _rooms_rows,
}


@login_required
def manage_view(request, section):
    """Renders one manage/list.html page per Management Panel tile / sidebar link.

    `section` comes from the url() kwargs set in slots/urls.py (e.g.
    path('manage/users/', views.manage_view, {'section': 'users'}, name='manage_users')),
    so one view backs every dashboard:manage_* route. This view is GET-only
    (listing); every section's add/edit/delete has its own dedicated view
    below (no shared Form/ModelForm class, no generic dispatcher).
    """
    title = MANAGE_SECTIONS.get(section, section.replace('_', ' ').title())
    rows_fn = ROWS_FUNCTIONS.get(section)

    if rows_fn:
        headers, rows = rows_fn()
        add_url = reverse(f'dashboard:manage_{section}_add')
    else:
        headers = DEFAULT_HEADERS.get(section, ['Name'])
        rows = []  # no model built for this section yet
        add_url = None

    return render(request, 'manage/list.html', {
        'title': title,
        'headers': headers,
        'rows': rows,
        'add_url': add_url,
        'manage_section': section,
    })


# ── University: plain HTML form, no Django Form/ModelForm class ───────────

def _university_form_context(request, university=None):
    errors = {}
    values = {
        'name': university.name if university else '',
        'code': university.code if university else '',
    }

    if request.method == 'POST':
        from .models import University

        is_edit = university is not None
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        values = {'name': name, 'code': code}

        if not name:
            errors['name'] = 'Name is required.'
        if not code:
            errors['code'] = 'Code is required.'

        if not errors:
            if university is None:
                university = University(name=name, code=code)
            else:
                university.name = name
                university.code = code
            university.save()
            messages.success(request, f'University {"updated" if is_edit else "created"} successfully.')
            return redirect('dashboard:manage_universities')

    return {
        'errors': errors,
        'values': values,
        'is_edit': university is not None,
        'back_url': reverse('dashboard:manage_universities'),
    }


@login_required
def university_add_view(request):
    result = _university_form_context(request)
    if not isinstance(result, dict):
        return result
    result['title'] = 'Add University'
    return render(request, 'manage/university_form.html', result)


@login_required
def university_edit_view(request, pk):
    from .models import University
    university = get_object_or_404(University, pk=pk)
    result = _university_form_context(request, university)
    if not isinstance(result, dict):
        return result
    result['title'] = 'Edit University'
    return render(request, 'manage/university_form.html', result)


@login_required
@require_POST
def university_delete_view(request, pk):
    from .models import University
    university = get_object_or_404(University, pk=pk)
    university.delete()
    messages.success(request, 'University deleted successfully.')
    return redirect('dashboard:manage_universities')


# ── Campus: plain HTML form, no Django Form/ModelForm class ────────────────
# The view reads request.POST.get(...) directly and builds/updates the model
# instance itself; validation is just plain if-checks, same pattern as the
# accounts:login view in user_management/views.py.

def _campus_form_context(request, campus=None):
    """Shared GET/POST handling for both add and edit -- returns either a
    redirect (on successful save) or a context dict to render the template with."""
    from .models import University, Campus

    universities = University.objects.all()
    errors = {}
    values = {
        'university': str(campus.university_id) if campus else '',
        'name': campus.name if campus else '',
        'code': campus.code if campus else '',
    }

    if request.method == 'POST':
        is_edit = campus is not None
        university_id = request.POST.get('university', '')
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        values = {'university': university_id, 'name': name, 'code': code}

        if not university_id:
            errors['university'] = 'University is required.'
        if not name:
            errors['name'] = 'Name is required.'
        if not code:
            errors['code'] = 'Code is required.'

        if not errors:
            if campus is None:
                campus = Campus(university_id=university_id, name=name, code=code)
            else:
                campus.university_id = university_id
                campus.name = name
                campus.code = code
            campus.save()
            messages.success(request, f'Campus {"updated" if is_edit else "created"} successfully.')
            return redirect('dashboard:manage_campuses')

    return {
        'universities': universities,
        'errors': errors,
        'values': values,
        'is_edit': campus is not None,
        'back_url': reverse('dashboard:manage_campuses'),
    }


@login_required
def campus_add_view(request):
    result = _campus_form_context(request)
    if not isinstance(result, dict):
        return result  # redirect after successful save
    result['title'] = 'Add Campus'
    return render(request, 'manage/campus_form.html', result)


@login_required
def campus_edit_view(request, pk):
    from .models import Campus
    campus = get_object_or_404(Campus, pk=pk)
    result = _campus_form_context(request, campus)
    if not isinstance(result, dict):
        return result
    result['title'] = 'Edit Campus'
    return render(request, 'manage/campus_form.html', result)


@login_required
@require_POST
def campus_delete_view(request, pk):
    from .models import Campus
    campus = get_object_or_404(Campus, pk=pk)
    campus.delete()
    messages.success(request, 'Campus deleted successfully.')
    return redirect('dashboard:manage_campuses')


# ── Room: plain HTML form, no Django Form/ModelForm class ──────────────────

def _room_form_context(request, room=None):
    from .models import Building, Room

    buildings = Building.objects.all()
    errors = {}
    values = {
        'building': str(room.building_id) if room else '',
        'room_id': room.room_id if room else '',
        'room_type': room.room_type if room else '',
        'seating_capacity': room.seating_capacity if room else '',
        'floor': room.floor if room else '',
        'is_available': room.is_available if room else True,
    }

    if request.method == 'POST':
        building_id = request.POST.get('building', '')
        room_id = request.POST.get('room_id', '').strip()
        room_type = request.POST.get('room_type', '')
        seating_capacity = request.POST.get('seating_capacity', '').strip()
        floor = request.POST.get('floor', '').strip()
        is_available = request.POST.get('is_available') == 'on'
        values = {
            'building': building_id, 'room_id': room_id, 'room_type': room_type,
            'seating_capacity': seating_capacity, 'floor': floor, 'is_available': is_available,
        }

        if not building_id:
            errors['building'] = 'Building is required.'
        if not room_id:
            errors['room_id'] = 'Room ID is required.'
        if room_type not in dict(Room.RoomType.choices):
            errors['room_type'] = 'Choose a valid room type.'
        if not seating_capacity.isdigit():
            errors['seating_capacity'] = 'Seating capacity must be a whole number.'

        if not errors:
            is_edit = room is not None
            if room is None:
                room = Room(
                    building_id=building_id, room_id=room_id, room_type=room_type,
                    seating_capacity=int(seating_capacity), floor=floor, is_available=is_available,
                )
            else:
                room.building_id = building_id
                room.room_id = room_id
                room.room_type = room_type
                room.seating_capacity = int(seating_capacity)
                room.floor = floor
                room.is_available = is_available
            room.save()
            messages.success(request, f'Room {"updated" if is_edit else "created"} successfully.')
            return redirect('dashboard:manage_rooms')

    return {
        'buildings': buildings,
        'room_types': Room.RoomType.choices,
        'errors': errors,
        'values': values,
        'is_edit': room is not None,
        'back_url': reverse('dashboard:manage_rooms'),
    }


@login_required
def room_add_view(request):
    result = _room_form_context(request)
    if not isinstance(result, dict):
        return result
    result['title'] = 'Add Room'
    return render(request, 'manage/room_form.html', result)


@login_required
def room_edit_view(request, pk):
    from .models import Room
    room = get_object_or_404(Room, pk=pk)
    result = _room_form_context(request, room)
    if not isinstance(result, dict):
        return result
    result['title'] = 'Edit Room'
    return render(request, 'manage/room_form.html', result)


@login_required
@require_POST
def room_delete_view(request, pk):
    from .models import Room
    room = get_object_or_404(Room, pk=pk)
    room.delete()
    messages.success(request, 'Room deleted successfully.')
    return redirect('dashboard:manage_rooms')


# ── Building: plain HTML form, no Django Form/ModelForm class ──────────────

def _building_form_context(request, building=None):
    from .models import Campus, Building
    campuses = Campus.objects.all()
    errors = {}
    values = {
        'campus': str(building.campus_id) if building else '',
        'name': building.name if building else '',
        'code': building.code if building else '',
    }

    if request.method == 'POST':
        is_edit = building is not None
        campus_id = request.POST.get('campus', '')
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        values = {'campus': campus_id, 'name': name, 'code': code}

        if not campus_id:
            errors['campus'] = 'Campus is required.'
        if not name:
            errors['name'] = 'Name is required.'
        if not code:
            errors['code'] = 'Code is required.'

        if not errors:
            if building is None:
                building = Building(campus_id=campus_id, name=name, code=code)
            else:
                building.campus_id = campus_id
                building.name = name
                building.code = code
            building.save()
            messages.success(request, f'Building {"updated" if is_edit else "created"} successfully.')
            return redirect('dashboard:manage_buildings')

    return {
        'campuses': campuses,
        'errors': errors,
        'values': values,
        'is_edit': building is not None,
        'back_url': reverse('dashboard:manage_buildings'),
    }


@login_required
def building_add_view(request):
    result = _building_form_context(request)
    if not isinstance(result, dict):
        return result
    result['title'] = 'Add Building'
    return render(request, 'manage/building_form.html', result)

@login_required
def building_edit_view(request, pk):
    from .models import Building
    building = get_object_or_404(Building, pk=pk)
    result = _building_form_context(request, building)
    if not isinstance(result, dict):
        return result
    result['title'] = 'Edit Building'
    return render(request, 'manage/building_form.html', result)


@login_required
@require_POST
def building_delete_view(request, pk):
    from .models import Building
    building = get_object_or_404(Building, pk=pk)
    print(pk)
    building.delete()
    messages.success(request, 'Building deleted successfully.')
    return redirect('dashboard:manage_buildings')


# ── Room Booking: plain HTML form, no Django Form/ModelForm class ──────────

def _booking_form_context(request, booking=None):
    from datetime import date
    from booking.models import RoomBookingRequest
    from user_management.models import User

    users = User.objects.all().order_by('username')
    errors = {}
    values = {
        'requested_by': str(booking.requested_by_id) if booking else '',
        'booking_date': booking.booking_date.isoformat() if booking else '',
        'purpose': booking.purpose if booking else '',
        'assigned_room': booking.assigned_room if booking else '',
        'status': booking.status if booking else 'PENDING',
    }

    if request.method == 'POST':
        is_edit = booking is not None
        requested_by_id = request.POST.get('requested_by', '')
        booking_date_raw = request.POST.get('booking_date', '').strip()
        purpose = request.POST.get('purpose', '')
        assigned_room = request.POST.get('assigned_room', '').strip()
        status = request.POST.get('status', '')
        values = {
            'requested_by': requested_by_id, 'booking_date': booking_date_raw,
            'purpose': purpose, 'assigned_room': assigned_room, 'status': status,
        }

        if not requested_by_id:
            errors['requested_by'] = 'Requestor is required.'
        booking_date = None
        if not booking_date_raw:
            errors['booking_date'] = 'Date is required.'
        else:
            try:
                booking_date = date.fromisoformat(booking_date_raw)
            except ValueError:
                errors['booking_date'] = 'Enter a valid date.'
        if purpose not in dict(RoomBookingRequest.Purpose.choices):
            errors['purpose'] = 'Choose a valid purpose.'
        if status not in dict(RoomBookingRequest.Status.choices):
            errors['status'] = 'Choose a valid status.'

        if not errors:
            if booking is None:
                booking = RoomBookingRequest(
                    requested_by_id=requested_by_id, booking_date=booking_date,
                    purpose=purpose, assigned_room=assigned_room, status=status,
                )
            else:
                booking.requested_by_id = requested_by_id
                booking.booking_date = booking_date
                booking.purpose = purpose
                booking.assigned_room = assigned_room
                booking.status = status
            booking.save()
            messages.success(request, f'Room booking {"updated" if is_edit else "created"} successfully.')
            return redirect('dashboard:manage_bookings')

    return {
        'users': users,
        'purposes': RoomBookingRequest.Purpose.choices,
        'statuses': RoomBookingRequest.Status.choices,
        'errors': errors,
        'values': values,
        'is_edit': booking is not None,
        'back_url': reverse('dashboard:manage_bookings'),
    }


@login_required
def booking_add_view(request):
    result = _booking_form_context(request)
    if not isinstance(result, dict):
        return result
    result['title'] = 'Add Room Booking'
    return render(request, 'manage/booking_form.html', result)


@login_required
def booking_edit_view(request, pk):
    from booking.models import RoomBookingRequest
    booking = get_object_or_404(RoomBookingRequest, pk=pk)
    result = _booking_form_context(request, booking)
    if not isinstance(result, dict):
        return result
    result['title'] = 'Edit Room Booking'
    return render(request, 'manage/booking_form.html', result)


@login_required
@require_POST
def booking_delete_view(request, pk):
    from booking.models import RoomBookingRequest
    booking = get_object_or_404(RoomBookingRequest, pk=pk)
    booking.delete()
    messages.success(request, 'Room booking deleted successfully.')
    return redirect('dashboard:manage_bookings')


# ── User: plain HTML form, no Django Form/ModelForm class ──────────────────
# (Django admin still uses UserRegistrationForm -- see user_management/admin.py
# -- but that's the admin site's own internal machinery, separate from these
# custom manage pages.)

def _clean_optional_int(raw):
    raw = (raw or '').strip()
    return int(raw) if raw else None


@login_required
def user_add_view(request):
    from user_management.models import User

    errors = {}
    values = {
        'username': '', 'email': '', 'first_name': '', 'last_name': '',
        'phone': '', 'emp_id': '', 'campus': '', 'dept_code': '',
    }

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        emp_id = request.POST.get('emp_id', '').strip()
        campus = request.POST.get('campus', '').strip()
        dept_code = request.POST.get('dept_code', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        values = {
            'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name,
            'phone': phone, 'emp_id': emp_id, 'campus': campus, 'dept_code': dept_code,
        }

        if not username:
            errors['username'] = 'Username is required.'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'That username is already taken.'
        if not email:
            errors['email'] = 'Email is required.'
        if phone and not phone.isdigit():
            errors['phone'] = 'Phone must contain digits only.'
        if first_name == " ":
            errors['first_name'] = 'First Name is Required'
        if last_name == " ":
            errors['last_name'] = 'Last Name is Required'
        if not password1:
            errors['password1'] = 'Password is required.'
        elif password1 != password2:
            errors['password2'] = 'Passwords do not match.'

        if not errors:
            User.objects.create_user(
                username=username, email=email, password=password1,
                first_name=first_name, last_name=last_name,
                phone=_clean_optional_int(phone), emp_id=emp_id or None,
                campus=campus or None, dept_code=dept_code or None,
            )
            messages.success(request, 'User created successfully.')
            return redirect('dashboard:manage_users')

    return render(request, 'manage/user_form.html', {
        'title': 'Add User',
        'errors': errors,
        'values': values,
        'is_edit': False,
        'back_url': reverse('dashboard:manage_users'),
    })


@login_required
def user_edit_view(request, pk):
    from user_management.models import User

    user_obj = get_object_or_404(User, pk=pk)
    errors = {}
    values = {
        'username': user_obj.username, 'email': user_obj.email,
        'first_name': user_obj.first_name, 'last_name': user_obj.last_name,
        'phone': user_obj.phone or '', 'emp_id': user_obj.emp_id or '',
        'campus': user_obj.campus or '', 'dept_code': user_obj.dept_code or '',
    }

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        emp_id = request.POST.get('emp_id', '').strip()
        campus = request.POST.get('campus', '').strip()
        dept_code = request.POST.get('dept_code', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        values = {
            'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name,
            'phone': phone, 'emp_id': emp_id, 'campus': campus, 'dept_code': dept_code,
        }

        if not username:
            errors['username'] = 'Username is required.'
        elif User.objects.filter(username=username).exclude(pk=user_obj.pk).exists():
            errors['username'] = 'That username is already taken.'
        if not email:
            errors['email'] = 'Email is required.'
        if phone and not phone.isdigit():
            errors['phone'] = 'Phone must contain digits only.'
        if (password1 or password2) and password1 != password2:
            errors['password2'] = 'Passwords do not match.'

        if not errors:
            user_obj.username = username
            user_obj.email = email
            user_obj.first_name = first_name
            user_obj.last_name = last_name
            user_obj.phone = _clean_optional_int(phone)
            user_obj.emp_id = emp_id or None
            user_obj.campus = campus or None
            user_obj.dept_code = dept_code or None
            if password1:
                user_obj.set_password(password1)
            user_obj.save()
            messages.success(request, 'User updated successfully.')
            return redirect('dashboard:manage_users')

    return render(request, 'manage/user_form.html', {
        'title': 'Edit User',
        'errors': errors,
        'values': values,
        'is_edit': True,
        'back_url': reverse('dashboard:manage_users'),
    })


@login_required
@require_POST
def user_delete_view(request, pk):
    from user_management.models import User

    user_obj = get_object_or_404(User, pk=pk)
    if user_obj.pk == request.user.pk:
        messages.error(request, "You can't delete your own account while logged in as it.")
        return redirect('dashboard:manage_users')
    user_obj.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('dashboard:manage_users')

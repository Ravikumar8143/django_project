from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from booking.models import RoomBookingRequest
from .models import User, UserGroups,EmployeeMaster
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group

def login(request):
    """Log in with email OR employee ID + password, using a plain HTML form
    (no Django Form class) -- see templates/accounts/login.html.

    1. Read 'email_or_emp_id' and 'password' straight off request.POST.
    2. authenticate() runs every backend listed in AUTHENTICATION_BACKENDS.
       EmailOrEmpIdBackend (see backends.py) looks the identifier up against
       username, email, and emp_id, then checks the password hash.
    3. On success, auth_login() stores the user's id in the session.
    """
    if request.user.is_authenticated:
        return redirect('accounts:home')

    error = None
    email_or_emp_id = ''
    if request.method == 'POST':
        email_or_emp_id = request.POST.get('email_or_emp_id')
        password = request.POST.get('password', '')
        user = authenticate(request, username=email_or_emp_id, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome, {user.get_full_name() or user.username}.')
            return redirect('accounts:home')
        error = 'Invalid email/employee ID or password. Please try again.'
    return render(request, 'accounts/login.html', {'error': error, 'email_or_emp_id': email_or_emp_id})


ROLE_DASHBOARD_TEMPLATES = {
    'admin': 'dashboard/admin.html',
    'hoi': 'dashboard/hoi.html',
    'hod': 'dashboard/hod.html',
    'faculty': 'dashboard/faculty.html',
}


@login_required
def admin_dashboard(request):
    # No academic/scheduling models exist yet (Course, Room, Section,
    # Timetable, ...) -- those stats sit at 0 until that schema gets built.
    # total_users, users_by_role, recent_bookings, and the booking counts
    # ARE real now: they come straight off User/UserGroups/RoomBookingRequest.

    from django.urls import reverse as _rev
    ctx = {
        'user': request.user,
        'role': 'admin',
        'title': 'System Admin Dashboard',
        'stats': {
            'total_users': User.objects.count(),
            'total_courses': 0,
            'total_rooms': 0,
            'total_sections': 0,
            'timetables': 0,
            'published_timetables': 0,
            'pending_bookings': RoomBookingRequest.objects.filter(status='PENDING').count(),
            'approved_bookings': RoomBookingRequest.objects.filter(status='APPROVED').count(),
        },
        'recent_bookings': RoomBookingRequest.objects.select_related('requested_by').order_by('-submitted_at')[:10],
        'timetable_list': [],
        'users_by_role': (
            UserGroups.objects.filter(is_active=True, is_block=False)
            .values('role').annotate(count=Count('id')).order_by('role')
        ),
        'quick_links': [
            ('bi-people-fill', 'Users', _rev('dashboard:manage_users')),
            ('bi-bank2', 'Universities', _rev('dashboard:manage_universities')),
            ('bi-geo-alt-fill', 'Campuses', _rev('dashboard:manage_campuses')),
            ('bi-building', 'Buildings', _rev('dashboard:manage_buildings')),
            ('bi-door-open-fill', 'Rooms', _rev('dashboard:manage_rooms')),
            ('bi-diagram-3-fill', 'Departments', _rev('dashboard:manage_departments')),
            ('bi-calendar3', 'Acad Years', _rev('dashboard:manage_academic_years')),
            ('bi-mortarboard-fill', 'Programs', _rev('dashboard:manage_programs')),
            ('bi-book-fill', 'Courses', _rev('dashboard:manage_courses')),
            ('bi-collection-fill', 'Sections', _rev('dashboard:manage_sections')),
            ('bi-clock-fill', 'Time Slots', _rev('dashboard:manage_timeslots')),
            ('bi-table', 'Timetables', _rev('dashboard:manage_timetables')),
            ('bi-person-lines-fill', 'Employee TT', _rev('dashboard:employee_timetable_list')),
            ('bi-calendar2-week-fill', 'TT Overview', _rev('dashboard:admin_timetable_overview')),
            ('bi-calendar2-check-fill', 'Bookings', _rev('dashboard:manage_bookings')),
        ],
    }
    return render(request, 'dashboard/admin.html', ctx)


@login_required
def hoi_dashboard(request):
    # No RoomBookingRequest/ApprovalAudit models exist yet, so pending
    # requests/decisions and the room/booking stats are empty/0 for now.
    ctx = {
        'user': request.user,
        'role': 'hoi',
        'title': 'Head of Institute Dashboard',
        'pending_requests': [],
        'pending_count': 0,
        'recent_decisions': [],
        'stats': {
            'pending': 0,
            'approved_today': 0,
            'total_rooms': 0,
            'cross_dept': 0,
        },
    }
    return render(request, 'dashboard/hoi.html', ctx)


@login_required
def hod_dashboard(request, membership):
    # dashboard/hod.html is written to be department-scoped: 'department' is
    # the thing that must change when you switch which group is active.
    # There's no real Department model yet, so membership.group (Django's
    # built-in auth Group -- e.g. "CSE Department") stands in for it: it has
    # .name, which the template already reads. faculty_list/sections/stats
    # stay empty/0 until a real academic schema exists to query them from.
    department = membership.group
    ctx = {
        'user': request.user,
        'role': 'hod',
        'department': department,
        'stats': {
            'faculty_count': 0,
            'sections_count': 0,
            'courses': 0,
        },
        'faculty_list': [],
        'sections': [],
    }
    return render(request, 'dashboard/hod.html', ctx)


@login_required
def home(request):
    # A user can have several UserGroups rows (e.g. HOD of CSE + Faculty of IT).
    # Never use a blocked one; prefer the one marked is_default=True, else fall
    # back to any other active one. This is the ONE place that decides "which
    # membership is active right now" -- every dashboard view downstream
    # (admin/hoi/hod) gets its data scoped from this same membership, so
    # switching groups in the topbar dropdown changes what's displayed here.
    membership = (
        UserGroups.objects.filter(user_id=request.user.id, is_active=True, is_block=False, is_default=True).first()
        or UserGroups.objects.filter(user_id=request.user.id, is_active=True, is_block=False).first()
    )
    role = membership.role.lower() if membership else None

    if role == 'admin':
        depart_wise = User.objects.values('dept_code').distinct()
        print(depart_wise)
        return admin_dashboard(request)
    if role == 'hoi':
        return hoi_dashboard(request)
    if role == 'hod':
        return hod_dashboard(request, membership)

    template_name = ROLE_DASHBOARD_TEMPLATES.get(role, 'accounts/dashboard_default.html')
    return render(request, template_name, {'user': request.user, 'role': role})


@require_POST
@login_required
def switch_group(request, membership_id):
    """The topbar 'switch group/role' dropdown posts here.

    Exactly one UserGroups row is active at a time (radio-button style):
    the clicked membership gets is_active=True, every other membership for
    this user gets is_active=False. membership_id does NOT need to already
    be active -- clicking a currently-inactive group activates it. home()
    reads is_active (via User.get_active_membership()) on the very next
    request, so the dashboard shown updates immediately.
    """
    membership = get_object_or_404(UserGroups, pk=membership_id, user=request.user, is_block=False)

    UserGroups.objects.filter(user=request.user).exclude(pk=membership.pk).update(is_active=False, is_default=False)
    membership.is_active = True
    membership.is_default = True
    membership.save(update_fields=['is_active', 'is_default'])

    role_label = User.ROLE_LABELS.get(membership.role.lower(), membership.role)
    messages.success(request, f'Switched to {role_label} — {membership.group.name}.')
    return redirect('accounts:home')


def logout_view(request):
    auth_logout(request)
    return redirect('accounts:login')


# def sync_gsb_employees(request):
#     faculty_group = Group.objects.get(id=1)   # auth_group id = 1
#     employees = EmployeeMaster.objects.using("GITAM").filter(
#         college_code="GSB",
#         campus="VSP"
#     )
#     for emp in employees:
#
#         user, created = User.objects.get_or_create(
#             username=emp.empid,
#             defaults={
#                 "first_name": emp.first_name,
#                 "last_name": emp.last_name,
#                 "email": emp.emailid,
#                 "phone": emp.mobile,
#                 "emp_id": emp.empid,
#                 "campus": emp.campus,
#                 "college_code": emp.college_code,
#                 "dept_code": emp.dept_code,
#                 "designation_code": emp.job_description,
#                 "emp_type": emp.job_type,
#                 "password": make_password(emp.mobile),
#                 "is_active": True,
#             }
#         )
#         UserGroups.objects.get_or_create(
#             user=user,
#             group=faculty_group,
#             defaults={
#                 "role": "faculty",
#                 "is_active": True,
#                 "is_default": True,
#                 "is_block": False,
#             }
#         )
#     return "Faculty users synced successfully."

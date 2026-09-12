from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import path
from django.views.generic import RedirectView, TemplateView

from . import views

app_name = 'dashboard'


class DashboardPage(LoginRequiredMixin, TemplateView):
    """Renders one of the pre-built dashboard/*.html templates.

    These templates don't have real data behind them yet (no Resource/Slot/
    Booking models are wired up in this app currently) -- missing context
    vars just render as empty lists/'-' in the template, so pages show
    empty states instead of crashing.
    """


urlpatterns = [
    path('', RedirectView.as_view(pattern_name='accounts:home'), name='index'),
    path('timetable/', DashboardPage.as_view(template_name='dashboard/timetable.html'), name='timetable'),
    path('rooms/', DashboardPage.as_view(template_name='dashboard/rooms.html'), name='rooms'),
    path('hoi/', DashboardPage.as_view(template_name='dashboard/hoi.html'), name='hoi'),
    # NOT 'admin/' -- that collides with Django's own /admin/ site (config/urls.py
    # registers path('admin/', admin.site.urls) first, so it always wins that match).
    path('admin-panel/', DashboardPage.as_view(template_name='dashboard/admin.html'), name='admin'),
    path('hod/', DashboardPage.as_view(template_name='dashboard/hod.html'), name='hod'),
    path('faculty/', DashboardPage.as_view(template_name='dashboard/faculty.html'), name='faculty'),
    path('student/', DashboardPage.as_view(template_name='dashboard/student.html'), name='student'),
    path('coordinator/', DashboardPage.as_view(template_name='dashboard/coordinator.html'), name='coordinator'),
    path('timetable-overview/', DashboardPage.as_view(template_name='dashboard/generic.html'), name='admin_timetable_overview'),

    # Every "Management Panel" tile and every templates/manage/layout.html sidebar
    # link routes through views.manage_view, which renders manage/list.html.
    # 'users' and 'bookings' show real rows (User / RoomBookingRequest);
    # everything else shows a real page with an empty table until its model exists.
    path('employee-timetable/', views.manage_view, {'section': 'employee_timetable_list'}, name='employee_timetable_list'),
    path('manage/users/', views.manage_view, {'section': 'users'}, name='manage_users'),
    # User add/edit/delete: plain HTML forms, not Django Form/ModelForm classes.
    path('manage/users/add/', views.user_add_view, name='manage_users_add'),
    path('manage/users/<int:pk>/edit/', views.user_edit_view, name='manage_users_edit'),
    path('manage/users/<int:pk>/delete/', views.user_delete_view, name='manage_users_delete'),
    path('manage/universities/', views.manage_view, {'section': 'universities'}, name='manage_universities'),
    # University add/edit/delete: plain HTML forms, not Django Form/ModelForm classes.
    path('manage/universities/add/', views.university_add_view, name='manage_universities_add'),
    path('manage/universities/<int:pk>/edit/', views.university_edit_view, name='manage_universities_edit'),
    path('manage/universities/<int:pk>/delete/', views.university_delete_view, name='manage_universities_delete'),
    path('manage/campuses/', views.manage_view, {'section': 'campuses'}, name='manage_campuses'),
    # Campus add/edit/delete: plain HTML forms, not Django Form/ModelForm classes.
    path('manage/campuses/add/', views.campus_add_view, name='manage_campuses_add'),
    path('manage/campuses/<int:pk>/edit/', views.campus_edit_view, name='manage_campuses_edit'),
    path('manage/campuses/<int:pk>/delete/', views.campus_delete_view, name='manage_campuses_delete'),
    path('manage/buildings/', views.manage_view, {'section': 'buildings'}, name='manage_buildings'),
    # Building add/edit/delete: plain HTML forms, not Django Form/ModelForm classes.
    path('manage/buildings/add/', views.building_add_view, name='manage_buildings_add'),
    path('manage/buildings/<int:pk>/edit/', views.building_edit_view, name='manage_buildings_edit'),
    path('manage/buildings/<int:pk>/delete/', views.building_delete_view, name='manage_buildings_delete'),
    path('manage/rooms/', views.manage_view, {'section': 'rooms'}, name='manage_rooms'),
    # Room add/edit/delete: plain HTML forms, not Django Form/ModelForm classes.
    path('manage/rooms/add/', views.room_add_view, name='manage_rooms_add'),
    path('manage/rooms/<int:pk>/edit/', views.room_edit_view, name='manage_rooms_edit'),
    path('manage/rooms/<int:pk>/delete/', views.room_delete_view, name='manage_rooms_delete'),
    path('manage/departments/', views.manage_view, {'section': 'departments'}, name='manage_departments'),
    path('manage/academic-years/', views.manage_view, {'section': 'academic_years'}, name='manage_academic_years'),
    path('manage/programs/', views.manage_view, {'section': 'programs'}, name='manage_programs'),
    path('manage/course-categories/', views.manage_view, {'section': 'course_categories'}, name='manage_course_categories'),
    path('manage/courses/', views.manage_view, {'section': 'courses'}, name='manage_courses'),
    path('manage/offerings/', views.manage_view, {'section': 'offerings'}, name='manage_offerings'),
    path('manage/sections/', views.manage_view, {'section': 'sections'}, name='manage_sections'),
    path('manage/timeslots/', views.manage_view, {'section': 'timeslots'}, name='manage_timeslots'),
    path('manage/timetables/', views.manage_view, {'section': 'timetables'}, name='manage_timetables'),
    path('manage/bookings/', views.manage_view, {'section': 'bookings'}, name='manage_bookings'),
    # Room booking add/edit/delete: plain HTML forms, not Django Form/ModelForm classes.
    path('manage/bookings/add/', views.booking_add_view, name='manage_bookings_add'),
    path('manage/bookings/<int:pk>/edit/', views.booking_edit_view, name='manage_bookings_edit'),
    path('manage/bookings/<int:pk>/delete/', views.booking_delete_view, name='manage_bookings_delete'),
]

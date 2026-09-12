from django.urls import path

from . import views

app_name = 'bookings'

urlpatterns = [
    path('calendar/', views.BookingPage.as_view(template_name='bookings/calendar.html'), name='calendar'),
    path('list/', views.BookingPage.as_view(template_name='bookings/list.html'), name='list'),
    path('create/', views.create_view, name='create'),
    path('availability/', views.availability_view, name='availability'),
]

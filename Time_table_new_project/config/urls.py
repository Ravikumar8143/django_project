"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user_management.urls')),
    path('bookings/', include('booking.urls')),
    path('', include('slots.urls')),
]

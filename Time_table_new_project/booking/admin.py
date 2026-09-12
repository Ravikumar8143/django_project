from django.contrib import admin

from .models import RoomBookingRequest


@admin.register(RoomBookingRequest)
class RoomBookingRequestAdmin(admin.ModelAdmin):
    list_display = ('requested_by', 'booking_date', 'purpose', 'assigned_room', 'status', 'submitted_at')
    list_filter = ('status', 'purpose')
    search_fields = ('requested_by__username', 'requested_by__email', 'assigned_room')
    date_hierarchy = 'booking_date'

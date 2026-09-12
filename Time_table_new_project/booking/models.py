from django.conf import settings
from django.db import models


class RoomBookingRequest(models.Model):
    class Purpose(models.TextChoices):
        EXAMINATION = 'EXAMINATION', 'Examination'
        SEMINAR = 'SEMINAR', 'Seminar'
        MEETING = 'MEETING', 'Meeting'
        WORKSHOP = 'WORKSHOP', 'Workshop'
        CLASS_MAKEUP = 'CLASS_MAKEUP', 'Class Make-up'
        OTHER = 'OTHER', 'Other'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        CANCELLED = 'CANCELLED', 'Cancelled'

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='booking_requests'
    )
    booking_date = models.DateField()
    purpose = models.CharField(max_length=20, choices=Purpose.choices, default=Purpose.OTHER)
    # Plain text for now (e.g. "6.2 (Lecture Hall, cap=60)") -- no Room model exists yet.
    assigned_room = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.requested_by} - {self.booking_date} ({self.status})'

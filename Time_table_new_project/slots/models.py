from django.db import models


class University(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Campus(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='campuses')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Building(models.Model):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='buildings')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name


class Room(models.Model):
    class RoomType(models.TextChoices):
        LECTURE_HALL = 'LECTURE_HALL', 'Lecture Hall'
        LAB = 'LAB', 'Lab'
        SEMINAR_ROOM = 'SEMINAR_ROOM', 'Seminar Room'
        OFFICE = 'OFFICE', 'Office'

    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='rooms')
    room_id = models.CharField(max_length=20)
    room_type = models.CharField(max_length=20, choices=RoomType.choices, default=RoomType.LECTURE_HALL)
    seating_capacity = models.PositiveIntegerField(default=0)
    floor = models.CharField(max_length=20, blank=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['building', 'room_id']

    def __str__(self):
        return f'{self.room_id} ({self.building.name})'

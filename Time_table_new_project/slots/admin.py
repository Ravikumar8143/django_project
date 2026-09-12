from django.contrib import admin

from .models import University, Campus, Building, Room


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'university')
    list_filter = ('university',)
    search_fields = ('name', 'code')


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'campus')
    list_filter = ('campus',)
    search_fields = ('name', 'code')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'building', 'room_type', 'seating_capacity', 'is_available')
    list_filter = ('room_type', 'is_available', 'building')
    search_fields = ('room_id',)

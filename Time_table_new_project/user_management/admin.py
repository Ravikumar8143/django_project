from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UserRegistrationForm
from .models import User, UserGroups


class UserGroupsInline(admin.TabularInline):
    model = UserGroups
    extra = 1


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = UserRegistrationForm
    model = User
    list_display = ('username', 'email', 'emp_id', 'dept_code', 'is_staff', 'is_active')
    list_filter = ('dept_code', 'is_staff', 'is_active')
    # 'groups' is excluded here on purpose: it's an M2M with a custom `through`
    # model (UserGroups) that carries extra fields (role, is_active, ...), and
    # Django can't render that as a normal admin widget -- UserGroupsInline
    # below is how memberships/roles get managed instead.
    filter_horizontal = ('user_permissions',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('College info', {
            'fields': (
                'phone', 'campus', 'college_code', 'dept_code',
                'designation_code', 'dept_email', 'emp_id', 'emp_type', 'doj',
            )
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('College info', {'fields': ('email', 'emp_id', 'dept_code')}),
    )
    inlines = [UserGroupsInline]


@admin.register(UserGroups)
class UserGroupsAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'is_active', 'is_default', 'is_block')
    list_filter = ('role', 'is_active', 'is_default', 'is_block')

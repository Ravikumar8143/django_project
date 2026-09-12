from django import template

register = template.Library()


@register.filter
def has_role(user, role_name):
    """Usage: {% if request.user|has_role:"admin" %}"""
    if not getattr(user, 'is_authenticated', False):
        return False
    return user.role == role_name.lower()


@register.simple_tag
def role_badge_class(role):
    return {
        'admin': 'bg-danger',
        'hoi': 'bg-dark',
        'hod': 'bg-primary',
        'faculty': 'bg-success',
        'student': 'bg-info',
        'coordinator': 'bg-warning text-dark',
    }.get(role, 'bg-secondary')

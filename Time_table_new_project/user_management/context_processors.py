def user_memberships(request):
    """Feeds the topbar 'switch group/role' dropdown in base.html on every page."""
    if request.user.is_authenticated:
        memberships = request.user.memberships.filter(is_block=False).select_related('group').order_by('group__name')
        return {'user_memberships': memberships}
    return {'user_memberships': None}

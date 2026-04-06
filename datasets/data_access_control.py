from django.db.models import Q
from .models import Response
from .constants import ROLE_ACCESS_POLICY


def get_response_queryset(user):
    """
    Returns a queryset of Response records scoped to what the user is allowed to see
    based on their role as defined in ROLE_ACCESS_POLICY.

    args:
        user (User): current user
    returns:
        QuerySet of Response objects the user is authorized to view
    """
    policy = ROLE_ACCESS_POLICY.get(user.role, {})
    raw_scope = policy.get('raw_scope', 'none')

    if raw_scope == 'all':
        return Response.objects.all()
    elif raw_scope == 'own':
        if user.school is None:
            return Response.objects.none()
        return Response.objects.filter(school=user.school)
    else:
        return Response.objects.none()


def get_aggregate_scopes(user):
    """
    Returns the list of scopes the user is allowed to aggregate data across,
    as defined in ROLE_ACCESS_POLICY.

    args:
        user (User): current user
    returns:
        List of scopes the user is allowed to aggregate data across

    """
    policy = ROLE_ACCESS_POLICY.get(user.role, {})
    return policy.get('aggregate_scopes', [])


def get_dashboard_queryset(user):
    """
    Returns a queryset of all the Response records the user may aggregate,
    args:
        user (User): current user
    returns:
        QuerySet of Response objects the user is authorized to aggregate
    """
    scopes = get_aggregate_scopes(user)

    if not scopes:
        return Response.objects.none()

    # 'all' supersedes every other scope — short-circuit immediately.
    if 'all' in scopes:
        print(f"User {user} has 'all' scope, returning all responses")
        return Response.objects.all()

    query = Q()

    if 'own' in scopes:
        print(f"User {user} has 'own' scope, adding filter for school {user.school}")
        if user.school is not None:
            query |= Q(school=user.school)

    if 'group' in scopes:
        print(f"User {user} has 'group' scope, adding filter for groups")
        if user.school is not None:
            query |= Q(school__groups__in=user.school.groups.all())

    if not query:
        print(f"User {user} has no valid scopes, returning empty queryset")
        # Scopes were listed but none could be resolved (e.g. school is None)
        return Response.objects.none()

    # distinct() is required because the 'group' join can produce duplicate rows
    # when a school belongs to more than one group.
    print (f"User {user} has scopes {scopes}, returning filtered responses")
    temp = Response.objects.filter(query).distinct()
    print(f"Query returned {temp.count()} responses")
    return temp


def can_view_raw(user):
    """Returns True if the user is allowed to view raw response data."""
    policy = ROLE_ACCESS_POLICY.get(user.role, {})
    return policy.get('raw_scope', 'none') != 'none'
from functools import wraps
from django.shortcuts import redirect

# custom decorator to check logged in user's role and allow/deny access based on that

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())

            # always allow superusers
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            user_role = getattr(request.user, 'role', '') or ''
            if user_role.lower() not in [r.lower() for r in roles]:
                return redirect('unauthorized')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

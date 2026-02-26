from django.core.exceptions import PermissionDenied
from functools import wraps

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
            
            if request.user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
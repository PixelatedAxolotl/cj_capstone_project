from django.shortcuts import redirect

# Restrict admin pages to internal admin users and superusers and redirect unathorized users to 403 page
class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if request.user.is_authenticated:
                if not request.user.is_superuser and getattr(request.user, 'role', None) != 'internal':
                    return redirect('unauthorized')
        return self.get_response(request)
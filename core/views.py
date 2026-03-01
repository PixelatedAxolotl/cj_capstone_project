from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .decorators import role_required

from django.http import JsonResponse
from accounts.models import School


class CustomLoginView(LoginView):
    template_name = 'core/login.html'


def school_groups(request, school_id):
    try:
        school = School.objects.get(pk=school_id)
        groups = list(school.groups.values('name', 'group_type'))
        return JsonResponse({'groups': groups})
    except School.DoesNotExist:
        return JsonResponse({'groups': []})


@role_required('internal', 'school_admin')
def dashboard(request):
    return render(request, 'core/dashboard.html')

def unauthorized(request):
    return render(request, 'core/403.html')


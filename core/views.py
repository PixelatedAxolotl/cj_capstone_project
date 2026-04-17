from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.decorators import role_required

from django.http import JsonResponse

# Imports to display models on admin dashboard
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from accounts.models import User
from core.models import School, User_Group
from datasets.models import Dataset


def school_groups(request, school_id):
    try:
        school = School.objects.get(pk=school_id)
        groups = list(school.groups.values('name', 'group_type'))
        return JsonResponse({'groups': groups})
    except School.DoesNotExist:
        return JsonResponse({'groups': []})

@staff_member_required
def admin_index(request):
    context = {
        **admin.site.each_context(request),
        'users': User.objects.all(),
        'schools': School.objects.all(),
        'user_groups': User_Group.objects.all(),
        'datasets': Dataset.objects.all(),
    }
    return render(request, 'admin/index.html', context)


@role_required('internal', 'school_admin')
def dashboard(request):
    return render(request, 'core/dashboard.html')

def unauthorized(request):
    return render(request, 'core/403.html')


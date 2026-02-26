from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .decorators import role_required

class CustomLoginView(LoginView):
    template_name = 'core/login.html'


@role_required('internal', 'school_admin')
def dashboard(request):
    return render(request, 'core/dashboard.html')

def unauthorized(request):
    return render(request, 'core/403.html')
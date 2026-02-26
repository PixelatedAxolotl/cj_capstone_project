from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


class CustomLoginView(LoginView):
    template_name = 'core/login.html'


@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')
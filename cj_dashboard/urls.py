"""
URL configuration for cj_dashboard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views as core_views
from datasets import views as dataset_views

# Customize admin header bar
admin.site.site_header = "Career Jam Admin Dashboard"
admin.site.index_title = "Manage Users, Groups, and Datasets"

urlpatterns = [
    path('admin/upload-dataset/', dataset_views.upload_dataset, name='upload_dataset'),
    path('admin/', admin.site.urls),
    path('login/', core_views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', core_views.dashboard, name='dashboard'),
    path('unauthorized/', core_views.unauthorized, name='unauthorized'),
    path('school-groups/<int:school_id>/', core_views.school_groups, name='school_groups'),
]
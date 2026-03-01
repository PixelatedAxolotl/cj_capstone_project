from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib import admin
from . import views

# Customize admin header bar
admin.site.site_header = "Career Jam Admin Dashboard"
admin.site.index_title = "Manage Users, Groups, and Datasets"

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('unauthorized/', views.unauthorized, name='unauthorized'),

    path('school-groups/<int:school_id>/', views.school_groups, name='school_groups'),
]

handler403 = 'core.views.unauthorized'
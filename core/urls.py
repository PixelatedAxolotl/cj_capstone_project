from django.urls import path
from . import views

urlpatterns = [
    path('admin/',                         views.admin_index,   name='admin_index'),
    path('unauthorized/',                  views.unauthorized,  name='unauthorized'),
    path('school-groups/<int:school_id>/', views.school_groups, name='school_groups'),
]

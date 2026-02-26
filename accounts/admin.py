from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Group, School

# Register your models here.
admin.site.register(School)
admin.site.register(Group)
admin.site.register(User, UserAdmin)

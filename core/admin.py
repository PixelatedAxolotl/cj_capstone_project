from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup

# Register your models here.
# Unregister the default Group model so it is hidden from the admin interface
admin.site.unregister(AuthGroup)
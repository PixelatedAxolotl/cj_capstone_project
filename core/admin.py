from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup

from django.contrib.auth.forms import ReadOnlyPasswordHashWidget
from django.contrib.auth.admin import UserAdmin
from accounts.models import User, School, User_Group

#dataset imports
from datasets.models import Dataset
from django.shortcuts import redirect

# Register your models here.
# Unregister the default Group model so it is hidden from the admin interface
admin.site.unregister(AuthGroup)


# subclass ReadOnlyPasswordHashWidget to customize the password field display in the admin interface
class CustomReadOnlyPasswordHashWidget(ReadOnlyPasswordHashWidget):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['summary'] = [
            {'label': ''}
        ]
        return context


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('User Type & Affiliation', {'fields': ('role', 'school')}),
        ('User Status', {'fields': ('is_active',)}),
        #('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        #('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Role & Affiliation', {'fields': ('role', 'school')}),
        ('Account Status', {'fields': ('is_active',)}),
    )

    class Media:
        js = ('admin/js/user_admin.js',)

    # Override get_form to add help text for username field
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'username' in form.base_fields:
            form.base_fields['username'].help_text = 'Username should be unique and related to the institution the user is affiliated with (e.g. alb_high_admin1 for a school admin at Albany High School)'
        return form
    

# Redirect any attempt to access the default add form and instead load custom upload dataset view
class DatasetAdmin(admin.ModelAdmin):
    def add_view(self, request, form_url='', extra_context=None):
        return redirect('upload_dataset')

admin.site.register(User, CustomUserAdmin)
admin.site.register(School)
admin.site.register(User_Group)
admin.site.register(Dataset, DatasetAdmin)
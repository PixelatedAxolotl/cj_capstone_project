from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.forms import ReadOnlyPasswordHashWidget
from django.contrib.auth.admin import UserAdmin

from .models import User


# Hide the built-in Group model from the admin interface
admin.site.unregister(AuthGroup)
admin.site.enable_nav_sidebar = False


class InternalRolePermissionMixin:
    """Grant full admin permissions to internal role users and superusers, deny everyone else."""
    def _is_internal(self, request):
        return request.user.is_superuser or getattr(request.user, 'role', '').lower() == 'internal'

    def has_view_permission(self, request, obj=None):
        return self._is_internal(request)

    def has_change_permission(self, request, obj=None):
        return self._is_internal(request)

    def has_add_permission(self, request):
        return self._is_internal(request)

    def has_delete_permission(self, request, obj=None):
        return self._is_internal(request)


class CustomReadOnlyPasswordHashWidget(ReadOnlyPasswordHashWidget):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['summary'] = []
        return context


class CustomUserAdmin(InternalRolePermissionMixin, UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('User Type & Affiliation', {'fields': ('role', 'school')}),
        ('User Status', {'fields': ('is_active',)}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Role & Affiliation', {'fields': ('role', 'school')}),
        ('Account Status', {'fields': ('is_active',)}),
    )

    class Media:
        js = ('admin/js/user_admin.js',)
        css = {
            'all': ('css/admin/global.css',)
        }

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # Remove view/delete buttons next to School when embedded in change forms
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'school' and formfield and hasattr(formfield.widget, 'can_delete_related'):
            formfield.widget.can_delete_related = False
            formfield.widget.can_view_related = False
        return formfield

    def save_model(self, request, obj, form, change):
        obj.is_staff = (obj.role == 'internal')
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'username' in form.base_fields:
            form.base_fields['username'].help_text = (
                "Username should be unique and related to the institution the user is affiliated with "
                "(e.g. alb_high_admin1 for a school admin at Albany High School)"
            )
        if 'password' in form.base_fields:
            form.base_fields['password'].help_text = (
                "Passwords are encrypted for security, so there is no way to see the user's password. "
                "If a user has lost their password, you can set a new password for them here"
            )
        if 'is_active' in form.base_fields:
            form.base_fields['is_active'].help_text = (
                "Uncheck active status to disable user credentials. "
                "User will not be able to login or access the dashboard unless you reactivate their credentials."
            )
        return form


# TODO: add ability for regular users to reset their own passwords
# TODO: after save on change form go back to same tab rather than default users tab
admin.site.register(User, CustomUserAdmin)

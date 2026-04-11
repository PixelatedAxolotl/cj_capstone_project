from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup

from django.contrib.auth.forms import ReadOnlyPasswordHashWidget
from django.contrib.auth.admin import UserAdmin
from accounts.models import User, School, User_Group

#dataset imports
from datasets.models import Dataset, Question, Response, RespondentAnswer
from django.shortcuts import redirect
from django.db import transaction

# TODO: add ability for regular users to reset their own passwords
# Unregister the default Group model so it is hidden from the admin interface
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


# subclass ReadOnlyPasswordHashWidget to customize the password field display in the admin interface
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
        css = {
            'all': ('css/admin/global.css',)
        }

    # overrides Django default to get rid of view and delete buttons next to School
    # when school model field embedded in change forms (ex: user change form)
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'school' and formfield and hasattr(formfield.widget, 'can_delete_related'):
            formfield.widget.can_delete_related = False
            formfield.widget.can_view_related = False
        return formfield

    def save_model(self, request, obj, form, change):
        obj.is_staff = (obj.role == 'internal')
        super().save_model(request, obj, form, change)

    # Override get_form to add help text for username field
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'username' in form.base_fields:
            form.base_fields['username'].help_text = ("Username should be unique and related to the institution the user is affiliated with (e.g. alb_high_admin1 for a school admin at Albany High School)")

        if 'password' in form.base_fields:
            form.base_fields['password'].help_text = """Passwords are encrypted for security, so there is no way to see the user's password.
                                                        If a user has lost their password, you can set a new password for them here"""

        if 'is_active' in form.base_fields:
            form.base_fields['is_active'].help_text = """Uncheck active status to disable user credentials.
                                                      User will not be able to login or access the dashboard unless you reactive their credentials."""

        return form


class DatasetAdmin(InternalRolePermissionMixin, admin.ModelAdmin):
    # Redirect any attempt to access the default add form and instead load custom upload dataset view
    def add_view(self, request, form_url='', extra_context=None):
        return redirect('upload_dataset')

    # Redirect any attempt to access the default change form and instead load custom dataset detail view
    def change_view(self, request, object_id, form_url='', extra_context=None):
        return redirect('dataset_detail', dataset_id=object_id)


    def get_deleted_objects(self, objs, request):
        """
        Override to avoid the ORM Collector traversing all related objects
        for the confirmation page, which times out on large datasets.
        """
        dataset_ids = [obj.pk for obj in objs]

        perms_needed = set()

        # get counts to display to the user for delete confirmation
        summary = []
        for obj in objs:
            response_count = Response.objects.filter(dataset=obj).count()
            summary.append({'name': obj.name, 'response_count': response_count})

        return summary, {}, perms_needed, []


    # handles bulk-delete of datasets from the admin list view (checkbox + dropdown action)
    # overrides default delete behavior to avoid the ORM collector - subquery to reduce db hits and keep evaluation on db side instead of Python side
    def delete_queryset(self, request, queryset):
        """ Override default function to efficiently delete all Responses and RespondentAnswers related
            to the Datasets in the selected querysets without loading them into memory first."""
        with transaction.atomic():
            dataset_ids = list(queryset.values_list('pk', flat=True))

            # response_qs is not evaluated — it becomes a subquery in the DELETE
            response_qs = Response.objects.filter(dataset_id__in=dataset_ids)

            # Single SQL each: DELETE ... WHERE response_id IN (SELECT id FROM response WHERE dataset_id IN (...))
            RespondentAnswer.objects.filter(response__in=response_qs)._raw_delete(using='default')
            Response.objects.filter(dataset_id__in=dataset_ids)._raw_delete(using='default')
            queryset._raw_delete(using='default')

class QuestionAdmin(InternalRolePermissionMixin, admin.ModelAdmin):
    list_display  = ('label', 'question_type', 'can_crosstab', 'crosstab_label')
    list_editable = ('can_crosstab', 'crosstab_label')
    list_filter   = ('question_type', 'can_crosstab')
    search_fields = ('label', 'crosstab_label')

class SchoolAdmin(InternalRolePermissionMixin, admin.ModelAdmin):
    pass

class UserGroupAdmin(InternalRolePermissionMixin, admin.ModelAdmin):
    pass


# register models
admin.site.register(User, CustomUserAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(User_Group, UserGroupAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Question, QuestionAdmin)
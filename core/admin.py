from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup

from django.contrib.auth.forms import ReadOnlyPasswordHashWidget
from django.contrib.auth.admin import UserAdmin
from accounts.models import User, School, User_Group

#dataset imports
from datasets.models import Dataset, Response, RespondentAnswer
from django.shortcuts import redirect
from django.db import transaction

# Register your models here.
# Unregister the default Group model so it is hidden from the admin interface
admin.site.unregister(AuthGroup)


# subclass ReadOnlyPasswordHashWidget to customize the password field display in the admin interface
class CustomReadOnlyPasswordHashWidget(ReadOnlyPasswordHashWidget):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['summary'] = [
            {'label': 'Some Text Here'}
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

        # if 'password' in form.base_fields:
        #     form.base_fields['password'].widget = CustomReadOnlyPasswordHashWidget()

        return form

# class SchoolAdmin(admin.ModelAdmin):



class DatasetAdmin(admin.ModelAdmin):
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

        # Check permissions for each model being deleted
        perms_needed = set()
        if not request.user.has_perm('datasets.delete_response'):
            perms_needed.add('Response')
        if not request.user.has_perm('datasets.delete_respondentanswer'):
            perms_needed.add('RespondentAnswer')

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

admin.site.register(User, CustomUserAdmin)
admin.site.register(School)
admin.site.register(User_Group)
admin.site.register(Dataset, DatasetAdmin)
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

    def delete(self, request, obj):
        with transaction.atomic():
            RespondentAnswer.objects.filter(response__dataset_id=obj.pk)._raw_delete(using='default')
            Response.objects.filter(dataset_id=obj.pk)._raw_delete(using='default')
            obj.delete()

    # handles bulk-delete of datasets from the admin list view (checkbox + dropdown action)
    # overrides default to speed up deletion by deleting dependent records (respondentAnswer has response FK and response has dataset FK)
    #     This order means Django collector has nothing to load into memory and won't make deletions slow af 
    def delete_queryset(self, request, queryset):
        with transaction.atomic():
            dataset_ids = list(queryset.values_list('pk', flat=True))
            RespondentAnswer.objects.filter(response__dataset_id__in=dataset_ids)._raw_delete(using='default')
            Response.objects.filter(dataset_id__in=dataset_ids)._raw_delete(using='default')
            queryset.delete()

admin.site.register(User, CustomUserAdmin)
admin.site.register(School)
admin.site.register(User_Group)
admin.site.register(Dataset, DatasetAdmin)
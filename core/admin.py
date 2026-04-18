from django import forms
from django.contrib import admin

from accounts.admin import InternalRolePermissionMixin
from .models import School, User_Group


class UserGroupForm(forms.ModelForm):
    schools = forms.ModelMultipleChoiceField(
        queryset=School.objects.all().order_by('name'),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple('Schools', is_stacked=False),
        help_text='Select the schools that belong to this group.',
    )

    class Meta:
        model = User_Group
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['schools'].initial = self.instance.schools.all()


class SchoolAdmin(InternalRolePermissionMixin, admin.ModelAdmin):
    pass


class UserGroupAdmin(InternalRolePermissionMixin, admin.ModelAdmin):
    form = UserGroupForm

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.schools.set(form.cleaned_data.get('schools', []))

    class Media:
        css = {'all': ('admin/css/widgets.css',)}
        js = ('admin/js/core.js',)


admin.site.register(School, SchoolAdmin)
admin.site.register(User_Group, UserGroupAdmin)

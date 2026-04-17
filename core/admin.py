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
    pass


# register models
admin.site.register(User, CustomUserAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(User_Group, UserGroupAdmin)

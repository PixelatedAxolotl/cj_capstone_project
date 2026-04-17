from django.contrib import admin
from django.shortcuts import redirect
from django.db import transaction

from accounts.admin import InternalRolePermissionMixin
from .models import Dataset, Question, Response, RespondentAnswer


class DatasetAdmin(InternalRolePermissionMixin, admin.ModelAdmin):
    def add_view(self, request, form_url='', extra_context=None):
        # Redirect to custom upload view instead of the default add form
        return redirect('upload_dataset')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Redirect to custom dataset detail view instead of the default change form
        return redirect('dataset_detail', dataset_id=object_id)

    def get_deleted_objects(self, objs, request):
        """
        Override to avoid the ORM Collector traversing all related objects
        for the confirmation page, which times out on large datasets.
        """
        perms_needed = set()
        summary = []
        for obj in objs:
            response_count = Response.objects.filter(dataset=obj).count()
            summary.append({'name': obj.name, 'response_count': response_count})
        return summary, {}, perms_needed, []

    def delete_queryset(self, request, queryset):
        """
        Override default function to efficiently delete all Responses and RespondentAnswers
        related to the selected datasets without loading them into memory first.
        """
        with transaction.atomic():
            dataset_ids = list(queryset.values_list('pk', flat=True))
            response_qs = Response.objects.filter(dataset_id__in=dataset_ids)
            RespondentAnswer.objects.filter(response__in=response_qs)._raw_delete(using='default')
            Response.objects.filter(dataset_id__in=dataset_ids)._raw_delete(using='default')
            queryset._raw_delete(using='default')


class QuestionAdmin(InternalRolePermissionMixin, admin.ModelAdmin):
    list_display  = ('label', 'question_type', 'can_crosstab', 'crosstab_label')
    list_editable = ('can_crosstab', 'crosstab_label')
    list_filter   = ('question_type', 'can_crosstab')
    search_fields = ('label', 'crosstab_label')


admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Question, QuestionAdmin)

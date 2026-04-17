from django.urls import path
from . import views

urlpatterns = [
    path('summary_dashboard/',      views.dashboard_view,       name='dashboard'),
    path('summary_dashboard/data/', views.dashboard_data,       name='dashboard_data'),
    path('crosstab/tables/',        views.crosstab_tables_view, name='crosstab_tables'),
    path('crosstab/data/',          views.crosstab_data,        name='crosstab_data'),

    path('admin/upload-dataset/',                     views.upload_dataset,  name='upload_dataset'),
    path('admin/confirm-import/',                     views.confirm_import,  name='confirm_import'),
    path('admin/upload-complete/',                    views.upload_complete, name='upload_complete'),
    path('manage/datasets/<int:dataset_id>/',         views.dataset_detail,  name='dataset_detail'),
]

from django.contrib import admin
from django.urls import include, path

# Customize admin header bar
admin.site.site_header = "Career Jam Admin Dashboard"
admin.site.index_title = "Manage Users, Groups, and Datasets"

urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('', include('core.urls')),
    path('', include('accounts.urls')),
    path('', include('datasets.urls')),
    path('admin/', admin.site.urls),    #must be at the bottom so custom views intercept before built-in admin does
]
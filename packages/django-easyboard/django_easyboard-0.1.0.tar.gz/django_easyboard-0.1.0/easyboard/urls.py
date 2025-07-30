from django.urls import path, include
from .views import DashboardView, SettingsView, APIDocsView

app_name = 'easyboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('api-docs/', APIDocsView.as_view(), name='api_docs'),
    path('integration/import_export/', include('easyboard.integration.import_export.urls')),
    path('integration/mptt/', include('easyboard.integration.mptt.urls')),
] 
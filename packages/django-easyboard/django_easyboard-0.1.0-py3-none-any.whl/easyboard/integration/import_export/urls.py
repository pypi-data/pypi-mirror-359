from django.urls import path
from .views import ImportExportView

urlpatterns = [
    path('', ImportExportView.as_view(), name='import_export'),
] 
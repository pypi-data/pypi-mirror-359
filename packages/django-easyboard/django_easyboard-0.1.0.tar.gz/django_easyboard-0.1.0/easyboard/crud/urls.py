from django.urls import path
from .views import CRUDListView, CRUDCreateView, CRUDUpdateView, CRUDDeleteView

urlpatterns = [
    path('<str:app_label>/<str:model_name>/', CRUDListView.as_view(), name='crud_list'),
    path('<str:app_label>/<str:model_name>/add/', CRUDCreateView.as_view(), name='crud_add'),
    path('<str:app_label>/<str:model_name>/<int:pk>/edit/', CRUDUpdateView.as_view(), name='crud_edit'),
    path('<str:app_label>/<str:model_name>/<int:pk>/delete/', CRUDDeleteView.as_view(), name='crud_delete'),
] 
from django.urls import path
from .views import MPTTView

urlpatterns = [
    path('', MPTTView.as_view(), name='mptt'),
] 
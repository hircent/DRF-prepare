from django.urls import path
from .views import SuperAdminListView

urlpatterns = [
    path("accounts/",SuperAdminListView.as_view(),name="super-admin-list"),    
]
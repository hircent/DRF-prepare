from django.urls import path
from .views import UserListView

urlpatterns = [
    path("accounts/",UserListView.as_view(),name="super-admin-list"),    
]
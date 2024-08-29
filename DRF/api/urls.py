
from django.urls import path

from branches.views import BranchListView
from accounts.views import UserListView , UserCreateView , UserRUDView
from .views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)



urlpatterns = [
    # User 
    path("users/list/",UserListView.as_view(),name="user-list"), 
    path("users/create/",UserCreateView.as_view(),name="user-create"), 
    path("users/rud/<int:pk>",UserRUDView.as_view(),name="user-rud"), 
    
    #Branch
    path("branch/list/",BranchListView.as_view(),name="branch-list"),

    #Token
    path('login/', CustomTokenObtainPairView.as_view(), name='login_token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
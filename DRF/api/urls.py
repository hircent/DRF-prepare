
from django.urls import path

from accounts.views import UserListView , UserCreateView , UserRUDView
from branches.views import BranchListView ,BranchRUDView,BranchCreateView
from students.views import StudentListView
from .views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)



urlpatterns = [
    # User 
    path("users/list",UserListView.as_view(),name="user-list"), 
    path("users/create",UserCreateView.as_view(),name="user-create"), 
    path("users/<int:pk>",UserRUDView.as_view(),name="user-rud"), 
    
    #Branch DONE
    path("branch/list",BranchListView.as_view(),name="branch-list"),
    path("branch/create",BranchCreateView.as_view(),name="branch-create"),
    path("branch/<int:pk>",BranchRUDView.as_view(),name="branch-rud"),

    #Students
    path('students/list',StudentListView.as_view(),name='student-list'),
    
    #Token
    path('login', CustomTokenObtainPairView.as_view(), name='login_token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    
]

from django.urls import path

from accounts.views import RoleBasesUserListView,RoleBasedUserCreateView,RoleBasedUserDeleteView,RoleBasedUserUpdateView,RoleBasedUserDetailsView
from branches.views import BranchListView ,BranchRUDView,BranchCreateView
from students.views import StudentListView
from .views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)



urlpatterns = [
    path("users/<str:role>/branch/<int:branch_id>/list",RoleBasesUserListView.as_view(),name="user-role-based-list"), 
    path("users/<str:role>/details/<int:pk>/branch/<int:branch_id>",RoleBasedUserDetailsView.as_view(),name="user-details"), 
    path("users/create/<str:role>/branch/<int:branch_id>",RoleBasedUserCreateView.as_view(),name="create-user"), 
    path("users/update/<str:role>/<int:pk>/branch/<int:branch_id>",RoleBasedUserUpdateView.as_view(),name="update-user"), 
    path("users/delete/<str:role>/<int:pk>/branch/<int:branch_id>",RoleBasedUserDeleteView.as_view(),name="delete-user"), 
    
    # # Student 
    # path("student/list",ParentListView.as_view(),name="student-list"), 
    # path("student/create",UserCreateView.as_view(),name="student-create"), 
    # path("student/<int:pk>",UserRUDView.as_view(),name="student-rud"), 
    
    #Branch DONE
    path("branch/list",BranchListView.as_view(),name="branch-list"),
    path("branch/create",BranchCreateView.as_view(),name="branch-create"),
    path("branch/<int:pk>",BranchRUDView.as_view(),name="branch-rud"),

    #Token
    path('login', CustomTokenObtainPairView.as_view(), name='login_token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    
]

from django.urls import path

from accounts.views import RoleBasesUserListView,RoleBasedUserCreateView,RoleBasedUserDeleteView,RoleBasedUserUpdateView,RoleBasedUserDetailsView
from branches.views import BranchListView ,BranchCreateView,BranchRetrieveView,BranchUpdateView,BranchDeleteView
from students.views import StudentListView ,StudentDetailsView ,StudentCreateView,StudentUpdateView,StudentDeleteView
from .views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)



urlpatterns = [
    # Users for Superadmin, Principals, Managers, Teachers, Parents
    path("users/<str:role>/branch/<int:branch_id>/list",RoleBasesUserListView.as_view(),name="user-role-based-list"), 
    path("users/<str:role>/details/<int:pk>/branch/<int:branch_id>",RoleBasedUserDetailsView.as_view(),name="user-details"), 
    path("users/create/<str:role>/branch/<int:branch_id>",RoleBasedUserCreateView.as_view(),name="create-user"), 
    path("users/update/<str:role>/<int:pk>/branch/<int:branch_id>",RoleBasedUserUpdateView.as_view(),name="update-user"), 
    path("users/delete/<str:role>/<int:pk>/branch/<int:branch_id>",RoleBasedUserDeleteView.as_view(),name="delete-user"), 
    
    #Branch DONE
    path("branch/list",BranchListView.as_view(),name="branch-list"),
    path("branch/details/<int:branch_id>",BranchRetrieveView.as_view(),name="branch-details"),
    path("branch/create",BranchCreateView.as_view(),name="create-branch"),
    path("branch/update/<int:branch_id>",BranchUpdateView.as_view(),name="update-branch"),
    path("branch/delete/<int:branch_id>",BranchDeleteView.as_view(),name="delete-branch"),

    #Students
    path("student/list/branch/<int:branch_id>",StudentListView.as_view(),name="student-list"),
    path("student/details/<int:student_id>/branch/<int:branch_id>",StudentDetailsView.as_view(),name="student-details"),
    path("student/create/branch/<int:branch_id>",StudentCreateView.as_view(),name="create-student"),
    path("student/update/<int:student_id>/branch/<int:branch_id>",StudentUpdateView.as_view(),name="update-student"),
    path("student/delete/<int:student_id>/branch/<int:branch_id>",StudentDeleteView.as_view(),name="delete-student"),

    #Token
    path('login', CustomTokenObtainPairView.as_view(), name='login_token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    
]
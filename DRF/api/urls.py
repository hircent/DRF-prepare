
from django.urls import path

from accounts.views import RoleBasesUserListView
from branches.views import BranchListView ,BranchRUDView,BranchCreateView
from students.views import StudentListView
from .views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)



urlpatterns = [
    path("users/<str:role>/branch/<int:branch_id>/list",RoleBasesUserListView.as_view(),name="user-role-based-list"), 
    # Superadmin 
    # path("superadmin/list",SuperadminListView.as_view(),name="superadmin-list"), 
    # path("superadmin/create",UserCreateView.as_view(),name="superadmin-create"), 
    # path("superadmin/<int:pk>",UserRUDView.as_view(),name="superadmin-rud"), 
    
    # # Principal 
    # path("principal/list",PrincipalListView.as_view(),name="principal-list"), 
    # path("principal/create",UserCreateView.as_view(),name="principal-create"), 
    # path("principal/<int:pk>",UserRUDView.as_view(),name="principal-rud"), 
    
    # # Manager 
    # path("manager/list",ManagerListView.as_view(),name="manager-list"), 
    # path("manager/create",UserCreateView.as_view(),name="manager-create"), 
    # path("manager/<int:pk>",UserRUDView.as_view(),name="manager-rud"), 
    
    # # Teacher 
    # path("teacher/list",TeacherListView.as_view(),name="teacher-list"), 
    # path("teacher/create",UserCreateView.as_view(),name="teacher-create"), 
    # path("teacher/<int:pk>",UserRUDView.as_view(),name="teacher-rud"), 
    
    # # Parent 
    # path("parent/list",ParentListView.as_view(),name="parent-list"), 
    # path("parent/create",UserCreateView.as_view(),name="parent-create"), 
    # path("parent/<int:pk>",UserRUDView.as_view(),name="parent-rud"), 
    
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
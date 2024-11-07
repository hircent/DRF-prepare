from accounts.views import (
    RoleBasesUserListView,RoleBasedUserCreateView,RoleBasedUserDeleteView,
    RoleBasedUserUpdateView,RoleBasedUserDetailsView
)
from branches.views import (
    BranchListView ,BranchCreateView,BranchRetrieveView,BranchUpdateView,BranchDeleteView,
    CombinedPrincipalsAndBranchGradesView,BranchSelectorListView
)
from calendars.views import (
    CalendarListView,CalendarRetrieveView,CalendarDestroyView,CalendarCreateView,CalendarUpdateView
)
from students.views import (
    StudentListView ,StudentDetailsView ,StudentCreateView,StudentUpdateView,StudentDeleteView
)
from category.views import (
    CategoryListView, ThemeListView, GradeListView, CategoryRetrieveView,
    CategoryCreateView, ThemeRetrieveView, GradeRetrieveView, CategoryDestroyView,
    ThemeDestroyView, CategoryUpdateView, ThemeUpdateView, ThemeCreateView,
    GradeCreateView, GradeUpdateView, GradeDestroyView, CategorySelectionListView
)
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)

from .views import CustomTokenObtainPairView


urlpatterns = [
    # Users for Superadmin, Principals, Managers, Teachers, Parents
    path("users/<str:role>/list",RoleBasesUserListView.as_view(),name="user-role-based-list"), 
    path("users/details/<int:pk>",RoleBasedUserDetailsView.as_view(),name="user-details"), 
    path("users/create/<str:role>",RoleBasedUserCreateView.as_view(),name="create-user"), 
    path("users/update/<str:role>/<int:pk>",RoleBasedUserUpdateView.as_view(),name="update-user"), 
    path("users/delete/<str:role>/<int:pk>",RoleBasedUserDeleteView.as_view(),name="delete-user"), 
    
    #Branch
    path("branch/list",BranchListView.as_view(),name="branch-list"),
    path("branch/details/<int:branch_id>",BranchRetrieveView.as_view(),name="branch-details"),
    path("branch/create",BranchCreateView.as_view(),name="create-branch"),
    path("branch/update/<int:branch_id>",BranchUpdateView.as_view(),name="update-branch"),
    path("branch/delete/<int:branch_id>",BranchDeleteView.as_view(),name="delete-branch"),

    #Students
    path("student/list",StudentListView.as_view(),name="student-list"),
    path("student/details/<int:student_id>",StudentDetailsView.as_view(),name="student-details"),
    path("student/create",StudentCreateView.as_view(),name="create-student"),
    path("student/update/<int:student_id>",StudentUpdateView.as_view(),name="update-student"),
    path("student/delete/<int:student_id>",StudentDeleteView.as_view(),name="delete-student"),

    #Calendars
    path('calendars/list', CalendarListView.as_view(), name='calendar-list'),
    path('calendars/details/<int:calendar_id>', CalendarRetrieveView.as_view(), name='calendar-details'),
    path('calendars/delete/<int:calendar_id>', CalendarDestroyView.as_view(), name='delete-calendar'),
    path('calendars/update/<int:calendar_id>', CalendarUpdateView.as_view(), name='update-calendar'),
    path('calendars/create', CalendarCreateView.as_view(), name='create-calendar'),

    #Category
    path('category/list', CategoryListView.as_view(), name='category-list'),
    path('category/selection-list', CategorySelectionListView.as_view(), name='category-selection-list'),
    path('category/details/<int:category_id>', CategoryRetrieveView.as_view(), name='category-details'),
    path('category/create', CategoryCreateView.as_view(), name='create-category'),
    path('category/update/<int:category_id>', CategoryUpdateView.as_view(), name='update-category'),
    path('category/delete/<int:category_id>', CategoryDestroyView.as_view(), name='delete-category'),

    path('theme/list', ThemeListView.as_view(), name='theme-list'),
    path('theme/details/<int:theme_id>', ThemeRetrieveView.as_view(), name='theme-details'),
    path('theme/create', ThemeCreateView.as_view(), name='create-theme'),
    path('theme/delete/<int:theme_id>', ThemeDestroyView.as_view(), name='delete-theme'),
    path('theme/update/<int:theme_id>', ThemeUpdateView.as_view(), name='update-theme'),

    path('grade/list', GradeListView.as_view(), name='grade-list'),
    path('grade/details/<int:grade_id>', GradeRetrieveView.as_view(), name='grade-details'),
    path('grade/create', GradeCreateView.as_view(), name='create-grade'),
    path('grade/update/<int:grade_id>', GradeUpdateView.as_view(), name='update-grade'),
    path('grade/delete/<int:grade_id>', GradeDestroyView.as_view(), name='delete-grade'),

    #Others
    path("branch/principals/branch_grade",CombinedPrincipalsAndBranchGradesView.as_view(),name="principal-branch_grade-for-branch"),
    path("branch/selector",BranchSelectorListView.as_view(),name="branch-selector"),

    #Token
    path('login', CustomTokenObtainPairView.as_view(), name='login_token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    
]
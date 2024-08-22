
from django.urls import path

from branches.views import BranchListView
from accounts.views import UserListView , UserCreateView , UserRUDView
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)



urlpatterns = [
    path('blogpost/', views.BlogPostListCreate.as_view(),name="blogpost-view-create"),
    path('blogpostlist/', views.BlogPostList.as_view(),name="blogpost-list"),
    path('blogpost/<int:pk>/', views.BlogPostRetrieveUpdateDestroy.as_view(),name="blogpost-update-destroy"),

    # User 
    path("users/list/",UserListView.as_view(),name="user-list"), 
    path("users/create/",UserCreateView.as_view(),name="user-create"), 
    path("users/rud/<int:pk>",UserRUDView.as_view(),name="user-rud"), 
    
    #Branch
    path("branch/list/",BranchListView.as_view(),name="branch-list"),

    #Token
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
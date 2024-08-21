
from django.urls import path

from accounts.views import UserListView
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

    path("accounts/",UserListView.as_view(),name="super-admin-list"), 
    
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
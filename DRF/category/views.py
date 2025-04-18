from .models import Category, Theme
from .serializers import (
    CategoryListSerializer, ThemeListSerializer,
    CategoryDetailsSerializer, CategoryCreateUpdateSerializer, 
    ThemeDetailsSerializer, ThemeUpdateSerializer ,ThemeCreateSerializer
)

from accounts.permission import IsSuperAdmin
from api.global_customViews import BaseCustomListAPIView, BaseCustomThemeListAPIView, GenericViewWithExtractJWTInfo
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics,status
from rest_framework.response import Response

# Create your views here.
class CategoryListView(BaseCustomListAPIView):
    serializer_class = CategoryListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        year = self.request.query_params.get('year', None)
        queryset = Category.objects.all()
        if year:
            queryset = queryset.filter(year=year)
    
        return queryset

class CategorySelectionListView(GenericViewWithExtractJWTInfo,generics.ListAPIView):
    serializer_class = CategoryListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Category.objects.filter(is_active=True)
    
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })
    

class CategoryRetrieveView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailsSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'category_id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
class CategoryCreateView(generics.CreateAPIView):
    serializer_class = CategoryCreateUpdateSerializer
    permission_classes = [IsSuperAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateUpdateSerializer
    permission_classes = [IsSuperAdmin]
    lookup_field = 'id'
    lookup_url_kwarg = 'category_id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        updated_instance = self.get_object()
        updated_serializer = self.get_serializer(updated_instance)
        return Response({"success": True, "data": updated_serializer.data})
    
class CategoryDestroyView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    permission_classes = [IsSuperAdmin]
    lookup_field = 'id'
    lookup_url_kwarg = 'category_id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class ThemeListView(BaseCustomThemeListAPIView):
    serializer_class = ThemeListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Theme.objects.all()
        q = self.request.query_params.get('q', None)
        year = self.request.query_params.get('year', None)
        cat_name = self.request.query_params.get('category', None)

        if q:
            queryset = queryset.filter(category__id=q)

        if year and cat_name:
            queryset = queryset.filter(category__year=year,category__name=cat_name).order_by('-id')
    
        return queryset
    

class ThemeRetrieveView(generics.RetrieveAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeDetailsSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'theme_id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
class ThemeCreateView(generics.CreateAPIView):
    serializer_class = ThemeCreateSerializer
    permission_classes = [IsSuperAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)
    
class ThemeUpdateView(generics.UpdateAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeUpdateSerializer
    permission_classes = [IsSuperAdmin]
    lookup_field = 'id'
    lookup_url_kwarg = 'theme_id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"success": True, "data": serializer.data})

class ThemeDestroyView(generics.DestroyAPIView):
    queryset = Theme.objects.all()
    permission_classes = [IsSuperAdmin]
    lookup_field = 'id'
    lookup_url_kwarg = 'theme_id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Theme deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


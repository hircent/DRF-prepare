from rest_framework.generics import RetrieveAPIView,DestroyAPIView,CreateAPIView,UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status

from accounts.permission import IsManagerOrHigher
from api.global_customViews import (
    BaseCustomCalendarListView,BaseCustomCalendarView, GenericViewWithExtractJWTInfo,
    BaseCustomCalendarThemeLessonListView
)
from .models import Calendar , CalendarThemeLesson
from .serializers import CalendarListSerializer,CalendarThemeLessonListSerializer

# Create your views here.

class CalendarListView(BaseCustomCalendarListView):
    serializer_class = CalendarListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        branch_id = self.request.headers.get('BranchId')
        queryset = Calendar.objects.all()

        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        user_branch_roles = self.extract_jwt_info("branch_role")

        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)
        
        if year:    
            queryset = queryset.filter(year=year)
        if month:
            queryset = queryset.filter(month=month)

        if is_superadmin:
            return queryset.filter(branch_id=branch_id).distinct()
        else:
            
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                
                raise PermissionDenied("You don't have access to this branch or role.")
            else:
                return queryset.filter(branch_id=branch_id)

class CalendarRetrieveView(BaseCustomCalendarView,RetrieveAPIView):
    serializer_class = CalendarListSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
class CalendarDestroyView(BaseCustomCalendarView,DestroyAPIView):
    serializer_class = CalendarListSerializer
    permission_classes = [IsManagerOrHigher]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        id = instance.id
        self.perform_destroy(instance)
        return Response({"success": True, "message": f"Calendar {id} deleted successfully"})

class CalendarCreateView(GenericViewWithExtractJWTInfo,CreateAPIView):
    serializer_class = CalendarListSerializer
    permission_classes = [IsManagerOrHigher]
    
    def create(self, request, *args, **kwargs):
        branch_id = self.request.headers.get('BranchId')

        if not branch_id:
            raise PermissionDenied("Missing branch id.")

        user_branch_roles = self.extract_jwt_info("branch_role")
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        if not is_superadmin and not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
            raise PermissionDenied("You don't have access to this branch or role.")

        data = request.data.copy()
        data['branch_id'] = branch_id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

class CalendarUpdateView(BaseCustomCalendarView,UpdateAPIView):
    serializer_class = CalendarListSerializer
    permission_classes = [IsManagerOrHigher]
    
    def update(self, request, *args, **kwargs):
        branch_id = self.request.headers.get("BranchId")
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        data = request.data.copy()
        data['branch_id'] = branch_id
        serializer = self.get_serializer(instance, data=data, partial=partial)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "msg": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        
        return Response({
            "success": True,
            "data": "Update Successful."
        })

class CalendarThemeLessonListView(BaseCustomCalendarThemeLessonListView):
    serializer_class = CalendarThemeLessonListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        day = self.request.query_params.get('day')
        branch_id = self.request.headers.get('BranchId')
        queryset = CalendarThemeLesson.objects.all().order_by('lesson_date')

        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        user_branch_roles = self.extract_jwt_info("branch_role")

        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)
        
        if year:    
            queryset = queryset.filter(year=year)
        if month:
            queryset = queryset.filter(month=month)
        if day:
            queryset = queryset.filter(day=day)

        if is_superadmin:
            return queryset.filter(branch_id=branch_id).distinct()
        else:
            
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                
                raise PermissionDenied("You don't have access to this branch or role.")
            else:
                return queryset.filter(branch_id=branch_id)
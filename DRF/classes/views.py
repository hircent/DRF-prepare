import datetime
from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.global_customViews import BaseCustomListAPIView ,GenericViewWithExtractJWTInfo, BaseCustomClassView, BaseCustomListNoPaginationAPIView
from accounts.permission import IsManagerOrHigher
from calendars.models import Calendar
from django.db.models import Q
from rest_framework.views import APIView
from django.http import JsonResponse
from datetime import date, datetime ,timedelta

from .models import Class,StudentEnrolment,ClassLesson
from .serializers import (
    ClassListSerializer,StudentEnrolmentListSerializer,ClassCreateUpdateSerializer,ClassEnrolmentListSerializer,
    ClassLessonListSerializer
)

class ClassListView(BaseCustomListAPIView):
    serializer_class = ClassListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        branch_id = self.request.headers.get('BranchId')
        q = self.request.query_params.get('q', None)
        
        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        user_branch_roles = self.extract_jwt_info("branch_role")

        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)
        
        # query_set = User.objects.filter(users__role__name=role).exclude(id=self.request.user.id)
        query_set = Class.objects.filter(branch=int(branch_id))
        
        if q:
            query_set = query_set.filter(
                Q(name=q)  # Case-insensitive search
            )
        if is_superadmin:
            return query_set
        else:
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                
                raise PermissionDenied("You don't have access to this branch or role.")
            else:
                return query_set

class ClassDetailsView(BaseCustomClassView,RetrieveAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassListSerializer
    permission_classes = [IsManagerOrHigher]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

class ClassCreateView(GenericViewWithExtractJWTInfo,CreateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassCreateUpdateSerializer
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
        data['branch'] = int(branch_id)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

class ClassUpdateView(BaseCustomClassView,UpdateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassCreateUpdateSerializer
    permission_classes = [IsManagerOrHigher]

    def update(self, request, *args, **kwargs):
        branch_id = self.request.headers.get("BranchId")
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        data = request.data.copy()
        data['branch'] = int(branch_id)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
    
        self.perform_update(serializer)
        
        updated_instance = self.get_object()
        updated_serializer = self.get_serializer(updated_instance)
        
        return Response({
            "success": True,
            "data": updated_serializer.data
        })
    
class ClassDestroyView(BaseCustomClassView,DestroyAPIView):
    queryset = Class.objects.all()
    permission_classes = [IsManagerOrHigher]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        id = instance.id
        self.perform_destroy(instance)    
        return Response({"success": True, "message": f"Class {id} deleted successfully"})
    
# Create your views here.

class StudentEnrolmentListView(BaseCustomListAPIView):
    queryset = StudentEnrolment.objects.all()
    serializer_class = StudentEnrolmentListSerializer
    permission_classes = [IsAuthenticated]

class ClassLessonFutureListByDateView(BaseCustomListNoPaginationAPIView):
    serializer_class = ClassEnrolmentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        branch_id = self.request.headers.get('BranchId')

        if not branch_id:
            raise PermissionDenied("Missing branch id.")

        user_branch_roles = self.extract_jwt_info("branch_role")
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        date = self.request.query_params.get('date')
        if not date:
            raise PermissionDenied("Missing date.")
        
        date = datetime.strptime(date, '%Y-%m-%d').date()
        
        has_event = self._has_event(date,branch_id)

        print(f"has_event: {has_event}")

        all_classes = Class.objects.filter(branch__id=branch_id,day=date.strftime("%A")).order_by('start_time')

        if is_superadmin:
            return all_classes if not has_event else []
        else:
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                
                raise PermissionDenied("You don't have access to this branch or role.")
            else:
                return all_classes if not has_event else []
            
    def _has_event(self,date,branch_id):
        all_events = Calendar.objects.filter(branch_id=branch_id,year=date.year)

        blockedDate = []

        for event in all_events:
            
            start_date = event.start_datetime.date()
            end_date = event.end_datetime.date()

            if start_date == end_date:
                blockedDate.append(start_date)
            else:

                while start_date <= end_date:
                    blockedDate.append(start_date)
                    start_date += timedelta(days=1)
        
        return date in blockedDate
    
    def get_serializer_context(self):
        context =  super().get_serializer_context()
        checkDate = self.request.query_params.get('date')

        check_after_week = self._calculate_after_week(checkDate)

        context['check_after_week'] = check_after_week
        return context
    
    def _calculate_after_week(self,checkDate):
        today = date.today()
        parsed_date = datetime.strptime(checkDate, '%Y-%m-%d').date()

        days = (parsed_date - today).days

        check_after_week = days // 7

        return abs(check_after_week)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "past_lessons": False,
            "data": serializer.data
        })
    

class ClassLessonPastListByDateView(BaseCustomListNoPaginationAPIView):
    serializer_class = ClassLessonListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        branch_id = self.request.headers.get('BranchId')

        if not branch_id:
            raise PermissionDenied("Missing branch id.")

        user_branch_roles = self.extract_jwt_info("branch_role")
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        date = self.request.query_params.get('date')
        if not date:
            raise PermissionDenied("Missing date.")
        
        date = datetime.strptime(date, '%Y-%m-%d').date()
        
        all_classes = ClassLesson.objects.filter(branch__id=branch_id,date=date).order_by('start_datetime')
        
        if is_superadmin:
            return all_classes
        else:
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                
                raise PermissionDenied("You don't have access to this branch or role.")
            else:
                return all_classes
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "past_lessons": True,
            "data": serializer.data
        })
    
class ClassLessonListByDateView(APIView):
    
    def dispatch(self, request, *args, **kwargs):
        # Extract the date from request (assuming it's passed as a query parameter)
        date_str = request.GET.get('date')
        
        if not date_str:
            return JsonResponse({"error": "Date parameter is required"}, status=400)

        try:
            given_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # Check if any ClassLesson exists for the given date
        if ClassLesson.objects.filter(date=given_date).exists():
            # Use ClassLessonPastListByDateView if ClassLesson exists for the given date
            view = ClassLessonPastListByDateView.as_view()
        else:
            # Use ClassEnrolmentListByDateView otherwise
            view = ClassLessonFutureListByDateView.as_view()

        # Call the selected view
        return view(request, *args, **kwargs)
from typing import Set, Dict
from collections import defaultdict
from django.http.response import HttpResponse as HttpResponse
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.global_customViews import (
    BaseCustomListAPIView, GenericViewWithExtractJWTInfo, BaseCustomClassView, BaseCustomListNoPaginationAPIView,
    BaseCustomEnrolmentView, BaseVideoAssignmentView
)
from accounts.permission import IsManagerOrHigher
from calendars.models import Calendar
from django.db.models import Q
from django.utils import timezone
from rest_framework.views import APIView
from django.http import JsonResponse
from datetime import date, datetime ,timedelta

from .models import Class,StudentEnrolment,ClassLesson,EnrolmentExtension
from .serializers import (
    ClassListSerializer,StudentEnrolmentListSerializer,ClassCreateUpdateSerializer,ClassEnrolmentListSerializer,
    ClassLessonListSerializer,TimeslotListSerializer,StudentEnrolmentDetailsSerializer,EnrolmentLessonListSerializer,
    EnrolmentExtensionSerializer,VideoAssignmentListSerializer
)

'''
Class Views
'''
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
    

'''
Enrolment Views
'''
class StudentEnrolmentListView(BaseCustomListAPIView):
    queryset = StudentEnrolment.objects.all()
    serializer_class = StudentEnrolmentListSerializer
    permission_classes = [IsAuthenticated]

class StudentEnrolmentDetailView(BaseCustomEnrolmentView,RetrieveAPIView):
    serializer_class = StudentEnrolmentDetailsSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

class StudentEnrolmentUpdateView(BaseCustomEnrolmentView,UpdateAPIView):
    serializer_class = StudentEnrolmentDetailsSerializer
    permission_classes = [IsManagerOrHigher]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        data = request.data.copy()
        data['branch'] = int(self.request.headers.get('BranchId'))
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
    
        self.perform_update(serializer)
        
        updated_instance = self.get_object()
        updated_serializer = self.get_serializer(updated_instance)
        
        return Response({
            "success": True,
            "data": updated_serializer.data
        })

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
class StudentEnrolmentDeleteView(BaseCustomEnrolmentView,DestroyAPIView):
    permission_classes = [IsManagerOrHigher]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        id = instance.id
        self.perform_destroy(instance)    
        return Response({"success": True, "message": f"Student Enrolment {id} deleted successfully"})

'''
Class Lesson Views
'''
class BaseClassLessonView(BaseCustomListNoPaginationAPIView):
    def _has_event(self,date,branch_id):
        blockedDate = self._get_blocked_date(branch_id=branch_id,year=date.year)
        
        return date in blockedDate
    
    def _get_blocked_date(self, branch_id: int, year: int) -> Set[date]:
        events = Calendar.objects.filter(
            branch_id=branch_id,
            year=year
        ).values_list('start_datetime', 'end_datetime')
        
        blocked_dates = set()
        
        for start_datetime, end_datetime in events:
            start_date = start_datetime.date()
            end_date = end_datetime.date()
            
            # If single day event
            if start_date == end_date:
                blocked_dates.add(start_date)
            else:
                # Add all dates in range
                current_date = start_date
                while current_date <= end_date:
                    blocked_dates.add(current_date)
                    current_date += timedelta(days=1)
                    
        return blocked_dates
    
    def get_serializer_context(self):
        context =  super().get_serializer_context()
        checkDate = self.request.query_params.get('date')
        branch_id = self.request.headers.get('BranchId')

        date = datetime.strptime(checkDate, '%Y-%m-%d').date()
        blockedDate = self._get_blocked_date(branch_id=branch_id,year=date.year)

        check_after_week = self._calculate_after_week(date,blockedDate,branch_id)

        context['check_after_week'] = check_after_week
        return context
    
    def _calculate_after_week(self, check_date: date, blocked_dates: Set[date], branch_id: int) -> int:
        """
        Calculate the number of available weeks between today and check_date, 
        excluding blocked dates across multiple years.
        
        Args:
            check_date: Target date to check until
            blocked_dates: Set of blocked dates for the current year
            branch_id: Branch ID for fetching blocked dates of other years
            
        Returns:
            int: Number of available weeks
        """
        today = date.today()
        total_weeks = (check_date - today).days // 7
        
        # Early return if no weeks to check
        if total_weeks <= 0:
            return 0
            
        # Create a cache for blocked dates by year
        blocked_dates_by_year: Dict[int, Set[date]] = defaultdict(set)
        blocked_dates_by_year[check_date.year] = blocked_dates
        
        blocked_weeks = 0
        check_year = check_date.year
        
        for week_num in range(total_weeks):
            current_date = check_date - timedelta(weeks=week_num + 1)
            current_year = current_date.year
            
            # If we need blocked dates for a new year, fetch and cache them
            if current_year != check_year and current_year not in blocked_dates_by_year:
                blocked_dates_by_year[current_year] = set(
                    self._get_blocked_date(branch_id=branch_id, year=current_year)
                )
            
            # Check if the current date is blocked
            if current_date in blocked_dates_by_year[current_year]:
                blocked_weeks += 1
                
        return total_weeks - blocked_weeks
    
class SearchTimeSlotListView(BaseClassLessonView):
    serializer_class = TimeslotListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        branch_id = self.request.headers.get('BranchId')
        category_name = self.request.query_params.get('category')

        if not category_name:
            raise PermissionDenied("Missing category name.")
        
        if not branch_id:
            raise PermissionDenied("Missing branch id.")

        user_branch_roles = self.extract_jwt_info("branch_role")
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        date = self.request.query_params.get('date')
        if not date:
            raise PermissionDenied("Missing date.")
        
        date = datetime.strptime(date, '%Y-%m-%d').date()
        
        has_event = self._has_event(date,branch_id)

        all_classes = Class.objects.filter(branch__id=branch_id,day=date.strftime("%A"),name=category_name).order_by('start_time')

        if is_superadmin:
            return all_classes if not has_event else []
        else:
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                
                raise PermissionDenied("You don't have access to this branch or role.")
            else:
                return all_classes if not has_event else []


class ClassLessonFutureListByDateView(BaseClassLessonView):
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

        all_classes = Class.objects.filter(branch__id=branch_id,day=date.strftime("%A")).order_by('start_time')

        if is_superadmin:
            return all_classes if not has_event else []
        else:
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                
                raise PermissionDenied("You don't have access to this branch or role.")
            else:
                return all_classes if not has_event else []
    
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
    
class EnrolmentLessonListView(BaseCustomListNoPaginationAPIView):
    serializer_class = EnrolmentLessonListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        branch_id = self.request.headers.get('BranchId')
        enrolment_id = self.kwargs.get("enrolment_id")

        if not enrolment_id:
            raise PermissionDenied("Missing enrolment id.")
        
        if not branch_id:
            raise PermissionDenied("Missing branch id.")

        user_branch_roles = self.extract_jwt_info("branch_role")
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        student_lessons = StudentEnrolment.objects.get(id=enrolment_id).attendances.all()

        if is_superadmin:
            return student_lessons 
        else:
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                
                raise PermissionDenied("You don't have access to this branch or role.")
            else:
                return student_lessons

class EnrolmentExtendView(BaseCustomEnrolmentView,UpdateAPIView):
    serializer_class = EnrolmentExtensionSerializer
    permission_classes = [IsManagerOrHigher]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if not instance.is_active:
            return Response({
                "success": False,
                "msg": "Enrolment is not active, cannot extend."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            ext = EnrolmentExtension.objects.create(
                enrolment=instance, 
                branch=instance.branch, 
                start_date=timezone.now().date()
            )

            if ext:
                instance.remaining_lessons += 12
                instance.save()
                return Response({
                    "success": True,
                    "msg": "Enrolment extended successfully.",
                })
        except:
            return Response({
                "success": False,
                "msg": "Something went wrong."
                }, status=status.HTTP_404_NOT_FOUND)

class VideoAssignmentListView(BaseCustomListNoPaginationAPIView):
    serializer_class = VideoAssignmentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        branch_id = self.request.headers.get('BranchId')
        enrolment_id = self.kwargs.get("enrolment_id")

        if not enrolment_id:
            raise PermissionDenied("Missing enrolment id.")
        
        if not branch_id:
            raise PermissionDenied("Missing branch id.")

        user_branch_roles = self.extract_jwt_info("branch_role")
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        enrolment_videos = StudentEnrolment.objects.get(id=enrolment_id).video_assignments.all()

        if is_superadmin:
            return enrolment_videos 
        else:
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                
                raise PermissionDenied("You don't have access to this branch or role.")
            else:
                return enrolment_videos
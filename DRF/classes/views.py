from typing import Set, Dict
from collections import defaultdict
from django.http.response import HttpResponse as HttpResponse
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from api.global_customViews import (
    BaseCustomListAPIView, GenericViewWithExtractJWTInfo, BaseCustomClassView, BaseCustomListNoPaginationAPIView,
    BaseCustomEnrolmentView, BaseVideoAssignmentView, BaseAPIView
)
from accounts.permission import IsManagerOrHigher, IsTeacherOrHigher
from calendars.models import Calendar
from classes.models import StudentAttendance
from classes.service import EnrolmentService
from certificate.service import CertificateService
from django.db.models import Q, F, Case, When, Value
from django.db import transaction
from django.http import JsonResponse
from datetime import date, datetime ,timedelta
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from payments.service import PaymentService

from .models import Class,StudentEnrolment,ClassLesson,EnrolmentExtension,ReplacementAttendance,VideoAssignment
from .serializers import (
    ClassListSerializer,StudentEnrolmentListSerializer,ClassCreateUpdateSerializer,ClassEnrolmentListSerializer,
    ClassLessonListSerializer,TimeslotListSerializer,StudentEnrolmentDetailsSerializer,EnrolmentLessonListSerializer,
    EnrolmentExtensionSerializer,VideoAssignmentListSerializer,VideoAssignmentDetailsSerializer,
    VideoAssignmentUpdateSerializer,TodayClassLessonSerializer,EnrolmentRescheduleClassSerializer,
    RescheduleClassListSerializer,EnrolmentAdvanceSerializer,TestLearnSerializer,
    StudentEnrolmentCreateSerializer,StudentEnrolmentUpdateSerializer,StudentEnrolmentDetailsForUpdateViewSerializer
)

import json

class TestLearnView(BaseCustomEnrolmentView,RetrieveAPIView):
    serializer_class = TestLearnSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

'''
Class Views
'''
class ClassListView(BaseCustomListAPIView):
    serializer_class = ClassListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        q = self.request.query_params.get('q', None)

        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)
        
        # query_set = User.objects.filter(users__role__name=role).exclude(id=self.request.user.id)
        query_set = Class.objects.filter(branch=int(branch_id))
        
        if q:
            query_set = query_set.filter(
                Q(name=q)  # Case-insensitive search
            )
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
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)
        
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
        branch_id = self.get_branch_id()
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
    
class RescheduleClassListView(BaseCustomListNoPaginationAPIView):
    serializer_class = RescheduleClassListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)
        name = self.request.query_params.get('category_name', None)
        day = self.request.query_params.get('day', None)
        
        self.require_query_param(name,"category name")
        self.require_query_param(day,"day")
        
        query_set = Class.objects.filter(branch=int(branch_id),name=name,day=day)

        return query_set

'''
Enrolment Views
'''
class StudentEnrolmentListView(BaseCustomListAPIView):
    serializer_class = StudentEnrolmentListSerializer
    permission_classes = [IsTeacherOrHigher]

    def get_queryset(self):
        is_active_param = self.request.query_params.get('is_active', 'true')
        is_active = is_active_param.lower() == 'true'
        category = self.request.query_params.get('category', None)
        name = self.request.query_params.get('name', None)

        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)

        if name:
            queryset = StudentEnrolment.objects.filter(
                branch=int(branch_id),
                student__fullname__icontains=name,
                student__status='IN_PROGRESS'
            ).select_related("student", "grade")
        else:
            queryset = StudentEnrolment.objects.filter(
                branch=int(branch_id),
                is_active=is_active,
                student__status='IN_PROGRESS'
            ).select_related("student", "grade")

        if category:
            queryset = queryset.filter(grade__category=category.upper())
        
        # First, get all objects and calculate end dates
        all_objects = list(queryset)
        
        # Create temporary dictionary with end_dates for each object
        temp_serializer = self.get_serializer()
        end_dates = {}
        
        for obj in all_objects:
            # Get the end date as a string in YYYY-MM-DD format
            date_str = temp_serializer.get_end_date(obj)
            # Convert to datetime for proper sorting
            end_date = datetime.strptime(date_str.strftime("%Y-%m-%d"), "%Y-%m-%d").date()
            end_dates[obj.id] = end_date
        

        sorted_objects = sorted(all_objects, key=lambda x: end_dates[x.id])
        
        # Return the sorted list as queryset
        return sorted_objects
        
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
        
        data = sorted(data, key=lambda x: x['end_date'])
        
        if page is not None:
            return self.get_paginated_response(data)
        
        return Response({
            "success": True,
            "data": data
        })
    
class StudentEnrolmentCreateView(BaseCustomEnrolmentView, CreateAPIView):
    serializer_class = StudentEnrolmentCreateSerializer
    permission_classes = [IsManagerOrHigher]

    def create(self, request, *args, **kwargs):
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)
        
        data = request.data.copy()
        data['branch'] = int(branch_id)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

class StudentEnrolmentDetailView(BaseCustomEnrolmentView,RetrieveAPIView):
    serializer_class = StudentEnrolmentDetailsForUpdateViewSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

class StudentEnrolmentUpdateView(BaseCustomEnrolmentView,UpdateAPIView):
    serializer_class = StudentEnrolmentUpdateSerializer
    permission_classes = [IsManagerOrHigher]

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            branch_id = self.get_branch_id()
            self.branch_accessible(branch_id)
            instance = self.get_object()

            if instance.student.status != 'IN_PROGRESS':
                return Response({
                    "success": False,
                    "msg": "Student is not in progress, cannot update."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            enrolments = StudentEnrolment.objects.filter(student_id=instance.student.id,is_active=True).exclude(id=instance.id).exists()
            
            if enrolments:
                return Response({
                    "success": False,
                    "msg": "Student has active enrolment, cannot update."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
        
            self.perform_update(serializer)
            
            updated_instance = self.get_object()
            updated_serializer = self.get_serializer(updated_instance)
            
            return Response({
                "success": True,
                "data": updated_serializer.data
            })
        
        except ValidationError as e:
            # Extracts the first error message
            error_message = " ".join(
                [str(msg) for field, messages in e.detail.items() for msg in messages]
            )
            return Response({
                "success": False,
                "msg": error_message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                "success": False,
                "msg": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
class StudentEnrolmentDeleteView(BaseCustomEnrolmentView,DestroyAPIView):
    permission_classes = [IsManagerOrHigher]

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            id = instance.id
            student_id = instance.student.id
            grade_level = instance.grade.grade_level

            PaymentService.void_payments(
                enrolment_ids=[id],
                description=f"Student {instance.student.fullname}'s enrolment has been deleted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            self.perform_destroy(instance)    

            EnrolmentService.activate_latest_enrolment(student_id)
            CertificateService.destory_certificate(student_id,grade_level)

            return Response({"success": True, "message": f"Student Enrolment {id} deleted successfully"})
        except Exception as e:
            return Response({"success": False, "message": f"Error deleting student enrolment: {str(e)}"})

class EnrolmentRescheduleClassView(BaseCustomEnrolmentView,UpdateAPIView):
    serializer_class = EnrolmentRescheduleClassSerializer
    permission_classes = [IsManagerOrHigher]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if not instance.is_active:
            return Response({
                "success": False,
                "msg": "Enrolment is not active, cannot reschedule."
            }, status=status.HTTP_400_BAD_REQUEST)
    
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        serializer.is_valid(raise_exception=True)
    
        self.perform_update(serializer)

        updated_instance = self.get_object()
        updated_serializer = self.get_serializer(updated_instance)

        return Response({
            "success": True,
            "data": updated_serializer.data
        })
        
class EnrolmentAdvanceView(BaseCustomEnrolmentView,CreateAPIView):
    serializer_class = EnrolmentAdvanceSerializer
    permission_classes = [IsManagerOrHigher]

    def create(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            if instance.grade.grade_level == 6:
                return Response({
                    "success":False,
                    "msg":"This is last grade of enrolment, unable to further advance"
                })

            if not self._check_is_payment_paid():
                return Response({
                    "success": True,
                    "msg": "Enrolment is not paid or fully paid, cannot advance."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            data = request.data.copy()
            data['enrolment_id'] = instance.id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            new_enrolment = serializer.save()

            updated_serializer = self.get_serializer(new_enrolment)

            return Response({
                "success": True,
                "data": updated_serializer.data
            })
        except ValidationError as e:
            error_detail = e.detail
            if isinstance(error_detail, dict) and "message" in error_detail:
                # Handle our custom formatted errors
                return Response({
                    "success": False,
                    "msg": error_detail["message"]
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Handle other validation errors
                return Response({
                    "success": False,
                    "msg": str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "success": False,
                "msg": "An unexpected error occurred"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            year=year,
            entry_type='centre holiday'
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
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)
        category_name = self.request.query_params.get('category')
        date = self.request.query_params.get('date')

        self.require_query_param(category_name,"category name")
        self.require_query_param(date,"date")
        
        date = datetime.strptime(date, '%Y-%m-%d').date()
        
        has_event = self._has_event(date,branch_id)

        all_classes = Class.objects.filter(branch__id=branch_id,day=date.strftime("%A"),name=category_name).order_by('start_time')

        return all_classes if not has_event else []


class ClassLessonFutureListByDateView(BaseClassLessonView):
    serializer_class = ClassEnrolmentListSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['date'] = self.request.query_params.get('date')
        return context

    def get_queryset(self):
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)

        date = self.request.query_params.get('date')
        self.require_query_param(date,"date")
        
        date = datetime.strptime(date, '%Y-%m-%d').date()
        
        has_event = self._has_event(date,branch_id)

        all_classes = Class.objects.filter(branch__id=branch_id,day=date.strftime("%A")).order_by('start_time')

        return all_classes if not has_event else []
    
class ClassLessonPastListByDateView(BaseCustomListNoPaginationAPIView):
    serializer_class = ClassLessonListSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['date'] = self.request.query_params.get('date')
        return context

    def get_queryset(self):
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)

        date = self.request.query_params.get('date')
        self.require_query_param(date,"date")
        
        date = datetime.strptime(date, '%Y-%m-%d').date()
        
        all_classes = ClassLesson.objects.filter(branch__id=branch_id,date=date).order_by('class_instance__start_time')
        
        return all_classes
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "past_lessons": True,
            "data": serializer.data
        })
    
class ClassLessonTodayListByDateView(BaseClassLessonView):
    serializer_class = TodayClassLessonSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['date'] = self.request.query_params.get('date')
        return context

    def get_queryset(self):
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)

        date = self.request.query_params.get('date')
        self.require_query_param(date,"date")
        
        today = datetime.strptime(date, '%Y-%m-%d').date()

        has_event = self._has_event(today, branch_id)
        
        if has_event:
            return ClassLesson.objects.none()
        
        # First check for existing class lessons
        existing_lessons = ClassLesson.objects.filter(
            branch_id=branch_id,
            date=today
        ).select_related('class_instance')
        
        # Get all classes for today
        today_classes = Class.objects.filter(
            branch_id=branch_id,
            day=today.strftime("%A")
        ).order_by('start_time')
        
        # Create missing lessons
        existing_class_ids = set(lesson.class_instance_id for lesson in existing_lessons)
        lessons_to_create = []
        
        for class_instance in today_classes:
            if class_instance.id not in existing_class_ids:
                lessons_to_create.append(
                    ClassLesson(
                        branch_id=branch_id,
                        class_instance=class_instance,
                        date=today,
                        start_datetime=datetime.combine(today, class_instance.start_time),
                        end_datetime=datetime.combine(today, class_instance.end_time)
                    )
                )
        
        if lessons_to_create:
            ClassLesson.objects.bulk_create(lessons_to_create)
            
        # Get all lessons for today after creation
        all_lessons = ClassLesson.objects.filter(
            branch_id=branch_id,
            date=today
        ).order_by('class_instance__start_time')
            
        return all_lessons

    
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

        today = datetime.today().date()

        # If past date
        if given_date < today:
            # Use ClassLessonPastListByDateView if ClassLesson exists for the given date
            view = ClassLessonPastListByDateView.as_view()

        # If future date
        elif given_date > today:
            # Use ClassEnrolmentListByDateView otherwise
            view = ClassLessonFutureListByDateView.as_view()

        # If today's date
        else:
            view = ClassLessonTodayListByDateView.as_view()

        # Call the selected view
        return view(request, *args, **kwargs)
    
class EnrolmentLessonListView(BaseCustomListNoPaginationAPIView):
    serializer_class = EnrolmentLessonListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)
        enrolment_id = self.kwargs.get("enrolment_id")

        self.require_id(enrolment_id,"enrolment id")

        student_lessons = StudentEnrolment.objects.get(id=enrolment_id).attendances.all().order_by('date')

        return student_lessons

class EnrolmentExtendView(BaseCustomEnrolmentView,UpdateAPIView):
    serializer_class = EnrolmentExtensionSerializer
    permission_classes = [IsManagerOrHigher]

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        require_start_date = request.data.get('start_date')
        self.require_query_param(require_start_date,'start date')
        start_date = datetime.strptime(require_start_date, '%Y-%m-%d').date()

        today = datetime.today().date()

        if start_date < today:
            return Response({
                "success": False,
                "msg": "Start date is less than today."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        is_today = start_date == today

        is_pending_ext = EnrolmentExtension.objects.filter(enrolment=instance,status='PENDING').exists()

        if is_pending_ext:
            return Response({
                "success": False,
                "msg": "There is an enrolment extension is pending, cannot extend further."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not self._check_is_payment_paid():
            return Response({
                "success": True,
                "msg": "Enrolment is not paid or fully paid, cannot extend."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not instance.is_active:
            return Response({
                "success": False,
                "msg": "Enrolment is not active, cannot extend."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            ext = EnrolmentExtension.objects.create(
                enrolment=instance, 
                branch=instance.branch, 
                start_date=start_date
            )

            if ext:

                if is_today:
                    ext.status = 'EXTENDED'
                    ext.save()
                    instance.remaining_lessons += 12
                    instance.save()

                self._create_video_assignments_after_extend_enrolment(instance)

                half_price = instance.grade.price / 2
                pre_outstanding = PaymentService.get_pre_outstanding(instance)
                PaymentService.create_payment(
                    enrolment=instance,
                    amount=half_price,
                    pre_outstanding=pre_outstanding,
                    parent=instance.student.parent,
                    enrolment_type="EXTEND"
                )

                return Response({
                    "success": True,
                    "msg": "Enrolment extended successfully.",
                })
            
            
        except:
            return Response({
                "success": False,
                "msg": "Something went wrong."
                }, status=status.HTTP_404_NOT_FOUND)
        
    def _create_video_assignments_after_extend_enrolment(self,enrolment_instance):

        try:
            exisiting_video_assignments = VideoAssignment.objects.filter(enrolment_id=enrolment_instance)

            VideoAssignment.objects.create(
                enrolment=enrolment_instance,
                video_number=exisiting_video_assignments.count() + 1
            )

        except Exception as e:
            return Response({
                "success": False,
                "msg": "Failed to create video assignments"
                }, status=status.HTTP_404_NOT_FOUND)

class VideoAssignmentListView(BaseCustomListNoPaginationAPIView):
    serializer_class = VideoAssignmentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)
        enrolment_id = self.kwargs.get("enrolment_id")

        self.require_id(enrolment_id,"enrolment id")

        enrolment_videos = StudentEnrolment.objects.get(id=enrolment_id).video_assignments.all()

        return enrolment_videos
            
class VideoAssignmentDetailsView(BaseVideoAssignmentView,RetrieveAPIView):
    serializer_class = VideoAssignmentDetailsSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
class VideoAssignmentUpdateView(BaseVideoAssignmentView,UpdateAPIView):
    serializer_class = VideoAssignmentUpdateSerializer
    permission_classes = [IsManagerOrHigher]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
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
    
class MarkAttendanceView(BaseAPIView):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            branch_id = self.get_branch_id()
            date = self.request.query_params.get('date')

            self.require_query_param(date,"date")

            user_branch_roles = self.extract_jwt_info("branch_role")
            is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

            data = json.loads(request.body)

            class_lesson_id = data.get('classId') or data.get('class_lesson')
            teacher_id = data.get('teacherId') or data.get('teacher')
            class_status = data.get('status')
            co_teacher_id = data.get('coTeacherId') or data.get('co_teacher')
            student_enrolments = json.loads(data.get('student_enrolments'))
            theme_lesson_id = data.get('theme_lesson')

            class_lesson = ClassLesson.objects.get(id=class_lesson_id)

            if not is_superadmin:
                if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                    raise PermissionDenied("You don't have access to this branch or role.")

            if len(student_enrolments) > 6:
                raise PermissionDenied("You can only mark attendance for upto 6 students.")
            
            if class_status == "COMPLETED":
                self.update_attendance(student_enrolments,class_lesson)
            elif class_status == "PENDING":
                self.create_attendances(student_enrolments,class_lesson,branch_id,date)
                class_lesson.status = "COMPLETED"

            self._update_class(class_lesson,theme_lesson_id,teacher_id,co_teacher_id)

            return Response({'success': True,'msg': 'Attendance updated successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False, 
                'msg': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def update_attendance(self,enrolments,class_lesson_instance):
        try:
            for enrolment in enrolments:
                try:
                    attendance_id = enrolment.get('id')
                    enrolment_status = enrolment.get('status')
                    is_replacement_lesson = enrolment.get('is_replacement_lesson')
                except Exception as loop_error:
                    print(f"Error processing enrolment in update_attendance : {str(loop_error)}")
                    raise

                if is_replacement_lesson:
                    self._update_replacement_lesson(attendance_id,enrolment_status)
                else:

                    attendance = StudentAttendance.objects.get(
                        id=attendance_id, 
                        class_lesson=class_lesson_instance
                    )
                    
                    if enrolment_status in ['ATTENDED','ABSENT']:
                        self._update_attendance_for_attended_or_absent(attendance,enrolment_status)
                    elif enrolment_status == 'FREEZED':
                        self._update_attendance_for_freeze(attendance,enrolment_status)
                    elif enrolment_status == 'SFREEZED':
                        self._update_attendance_for_sfreeze(attendance,enrolment_status)
                    elif enrolment_status == 'REPLACEMENT':
                        self._update_attendance_for_replacement(
                            attendance,enrolment_status,
                            enrolment.get('replacement_date'),
                            enrolment.get('replacement_timeslot_class_id'),
                        )

        except Exception as e:
            raise Exception(f"Error while updating attendance: {str(e)}")
        
    def _update_attendance_for_attended_or_absent(self,attendance_instance,enrolment_status):
        try:
            attendance_status = attendance_instance.status
            enrolment = attendance_instance.enrollment
 
            if attendance_status == 'FREEZED':
                enrolment.freeze_lessons += 1
                enrolment.remaining_lessons -= 1
            elif attendance_status == 'SFREEZED':
                enrolment.remaining_lessons -= 1
            elif attendance_status == 'REPLACEMENT':
                self._delete_replacement_attendance(attendance_instance)
            enrolment.save()

            attendance_instance.status = enrolment_status
            attendance_instance.has_attended = enrolment_status == 'ATTENDED'
            attendance_instance.save()
                
        except Exception as e:
            raise Exception(f"Error updating attendance attended or absent: {str(e)}")
        
    def _update_attendance_for_freeze(self,attendance_instance,enrolment_status):
        try:
            attendance_status = attendance_instance.status
            enrolment = attendance_instance.enrollment
 
            if attendance_status in ['ATTENDED','ABSENT']:
                enrolment.remaining_lessons += 1
                enrolment.freeze_lessons -= 1
            elif attendance_status == 'SFREEZED':
                enrolment.freeze_lessons -= 1
            elif attendance_status == 'REPLACEMENT':
                enrolment.freeze_lessons -= 1
                enrolment.remaining_lessons += 1
                self._delete_replacement_attendance(attendance_instance)
            enrolment.save()

            attendance_instance.status = enrolment_status
            attendance_instance.has_attended = enrolment_status == 'ATTENDED'
            attendance_instance.save()
            
            
        except Exception as e:
            raise Exception(f"Error updating attendance freeze: {str(e)}")

    def _update_attendance_for_sfreeze(self,attendance_instance,enrolment_status):
        try:
            attendance_status = attendance_instance.status
            enrolment = attendance_instance.enrollment
 
            if attendance_status in ['ATTENDED','ABSENT']:
                enrolment.remaining_lessons += 1
            elif attendance_status == 'FREEZED':
                enrolment.freeze_lessons += 1
            elif attendance_status == 'REPLACEMENT':
                enrolment.freeze_lessons += 1
                self._delete_replacement_attendance(attendance_instance)
            
            enrolment.save()

            attendance_instance.status = enrolment_status
            attendance_instance.has_attended = enrolment_status == 'ATTENDED'
            attendance_instance.save()

        except Exception as e:
            raise Exception(f"Error updating attendance sfreeze: {str(e)}")
        
    def _update_attendance_for_replacement(self,attendance_instance,enrolment_status,replacement_date, replacement_timeslot_class_id):

        try:
            attendance_status = attendance_instance.status
            enrolment = attendance_instance.enrollment
 
            if attendance_status in ['ATTENDED','ABSENT']:
                enrolment.remaining_lessons += 1
            elif attendance_status == 'FREEZED':
                enrolment.freeze_lessons += 1
            
            enrolment.save()
            
            if attendance_status != 'REPLACEMENT':
                self._create_replacement_attendance_after_update(
                    attendance_instance, 
                    replacement_date, 
                    replacement_timeslot_class_id
                )
            else:
                replace_att = attendance_instance.replacement_attendances
                replace_att.class_instance_id = replacement_timeslot_class_id
                replace_att.date = replacement_date
                replace_att.save()

            attendance_instance.status = enrolment_status
            attendance_instance.has_attended = enrolment_status == 'ATTENDED'
            attendance_instance.save()
            
        except Exception as e:
            raise Exception(f"Error updating attendance replacement: {str(e)}")
        
    def _create_replacement_attendance_after_update(self, attendance_instance, replacement_date, replacement_timeslot_class_id):
        try:
            ReplacementAttendance.objects.create(
                attendances=attendance_instance,
                class_instance_id=replacement_timeslot_class_id,
                date=replacement_date
            )
            
        except Exception as e:
            raise Exception(f"Error creating replacement attendance: {str(e)}")
        
    def _delete_replacement_attendance(self, attendance_instance):
        try:
            replacement_attendance = ReplacementAttendance.objects.get(
                attendances=attendance_instance
            )
            replacement_attendance.delete()
        except Exception as e:
            raise Exception(f"Error deleting replacement attendance: {str(e)}")

    def create_attendances(self, enrolments, class_lesson_instance, branch_id, date):
        try:
            att_arr = []

            attend_or_absent_arr = []

            freeze_arr = []

            sfreeze_arr = []

            replacement_arr = []

            replacement_details_arr = []

            start_time = class_lesson_instance.class_instance.start_time
            end_time = class_lesson_instance.class_instance.end_time

            for enrolment in enrolments:
                try:
                    id = enrolment.get('id')
                    enrolment_status = enrolment.get('status')
                    is_replacement_lesson = enrolment.get('is_replacement_lesson')

                except Exception as loop_error:
                        print(f"Error processing enrolment in create_attendances: {str(loop_error)}")
                        raise

                if is_replacement_lesson:
                    self._update_replacement_lesson(id,enrolment_status)
                else:
                    try:
                        attendance = StudentAttendance(
                            enrollment_id=id,
                            branch_id=branch_id,
                            class_lesson=class_lesson_instance,
                            date=date,
                            day=class_lesson_instance.class_instance.day,
                            start_time=start_time,
                            end_time=end_time,
                            has_attended=enrolment_status == 'ATTENDED',
                            status=enrolment_status,
                        )
                        att_arr.append(attendance)

                        if enrolment_status in ['ATTENDED','ABSENT']:
                            attend_or_absent_arr.append(id)
                        elif enrolment_status == 'FREEZED':
                            freeze_arr.append(id)
                        elif enrolment_status == 'SFREEZED':
                            sfreeze_arr.append(id)
                        elif enrolment_status == 'REPLACEMENT':
                            replacement_arr.append(id)
                            replacement_details_arr.append({
                                'enrolment_id': id,
                                'replacement_date': enrolment.get('replacement_date'),
                                'replacement_timeslot_class_id': enrolment.get('replacement_timeslot_class_id'),
                                'date':date
                            })

                    except Exception as model_error:
                        print(f"Error creating attendance object: {str(model_error)}")
                        raise

                    

            if att_arr:
                StudentAttendance.objects.bulk_create(att_arr)

                self._update_enrolment_remaining_lesson_after_create_attendance(
                    attend_or_absent_arr,freeze_arr,sfreeze_arr,replacement_arr
                )

                if replacement_arr and replacement_details_arr:
                    self._create_replacement_attendance(replacement_details_arr)

        except Exception as e:
            raise Exception(f"Error while creating attendances: {str(e)}")
        
    def _update_class(self, class_lesson_instance,theme_lesson_id,teacher_id,co_teacher_id):
        class_lesson_instance.theme_lesson_id = theme_lesson_id
        class_lesson_instance.teacher_id = teacher_id

        if co_teacher_id:
            class_lesson_instance.co_teacher_id = co_teacher_id

        class_lesson_instance.save()

    def _update_enrolment_remaining_lesson_after_create_attendance(self,attend_or_absent_arr,freeze_arr,sfreeze_arr,replacement_arr):
        
        try:
            enrolments_to_update = []

            if attend_or_absent_arr:
                StudentEnrolment.objects.filter(
                    id__in=attend_or_absent_arr
                ).select_for_update().update(
                    remaining_lessons=F("remaining_lessons") - 1,
                    is_active=Case(
                        When(remaining_lessons=1, then=Value(False)), # When remaining_lessons becomes 0 after decrement
                        default=Value(True)
                    ),
                    status=Case(
                        When(remaining_lessons=1, then=Value('COMPLETED')), # When remaining_lessons becomes 0 after decrement
                        default=F('status')
                    )
                )

            if freeze_arr:
                student_enrolments = StudentEnrolment.objects.filter(
                    id__in=freeze_arr
                ).select_for_update()

                for se in student_enrolments:

                    if se.freeze_lessons <= 0:
                        raise ValueError(f"Enrolment {se.id} has exceeded freeze count")
                    
                    se.freeze_lessons = F("freeze_lessons") - 1
                
                    enrolments_to_update.append(se)
            
            if sfreeze_arr:
                # It should do ntg 
                pass
                # student_enrolments = StudentEnrolment.objects.filter(
                #     id__in=sfreeze_arr
                # ).select_for_update()

                # for se in student_enrolments:
                #     se.remaining_lessons = F("remaining_lessons") + 1

                #     enrolments_to_update.append(se)
            
            if replacement_arr:
                pass

            if enrolments_to_update:
                fields_to_update = ['remaining_lessons', 'is_active', 'status', 'freeze_lessons']
                StudentEnrolment.objects.bulk_update(
                    enrolments_to_update,
                    fields_to_update
                )
        
        except Exception as e:
            raise Exception(f"Error updating enrolment lessons: {str(e)}")
        
    def _create_replacement_attendance(self, replacement_details_arr):
        """
        Creates replacement attendance records for students
        Args:
            replacement_details_arr: List of dictionaries containing replacement details
            Each dict should have: enrolment_id, replacement_date, replacement_timeslot_class_id
        """
        replacement_arr = []
        
        try:
            # Validate input data
            if not replacement_details_arr or not isinstance(replacement_details_arr, list):
                raise ValueError("Invalid replacement details provided")

            # Process each replacement
            for replacement in replacement_details_arr:
                # Extract and validate required fields
                enrolment_id = replacement.get('enrolment_id')
                replacement_date_str = replacement.get('replacement_date')
                replacement_timeslot_class_id = replacement.get('replacement_timeslot_class_id')
                date = replacement.get('date')

                if not all([enrolment_id, replacement_date_str, replacement_timeslot_class_id]):
                    raise ValueError(f"Missing required fields for replacement: {replacement}")

                try:
                    replacement_date = datetime.strptime(replacement_date_str, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError(f"Invalid date format for replacement: {replacement_date_str}")

                # Get the student's attendance for the replacement date
                try:
                    student_enrolment_attendance = StudentAttendance.objects.filter(enrollment_id=enrolment_id,date=date).first()
                    
                    if not student_enrolment_attendance:
                        raise ValueError(f"No attendance found for student {enrolment_id} on {replacement_date}")

                    # Check if replacement already exists
                    existing_replacement = ReplacementAttendance.objects.filter(
                        attendances_id=student_enrolment_attendance.id,
                        date=replacement_date
                    ).exists()

                    if existing_replacement:
                        raise ValueError(f"Replacement already exists for student {enrolment_id} on {replacement_date}")

                    # Create new replacement attendance
                    replacement_attendance = ReplacementAttendance(
                        attendances_id=student_enrolment_attendance.id,
                        class_instance_id=replacement_timeslot_class_id,
                        date=replacement_date
                    )
                    replacement_arr.append(replacement_attendance)

                except StudentEnrolment.DoesNotExist:
                    raise ValueError(f"Student enrolment {enrolment_id} not found")
                except Exception as e:
                    raise ValueError(f"Error processing replacement for student {enrolment_id}: {str(e)}")

            # Bulk create all valid replacement attendances
            if replacement_arr:
                ReplacementAttendance.objects.bulk_create(replacement_arr)

        except Exception as e:
            raise Exception(f"Error creating replacement attendances: {str(e)}")

    def _update_replacement_lesson(self,replacement_id,status):
        try:

            replacement_att = ReplacementAttendance.objects.select_related(
                "attendances","attendances__enrollment").select_for_update().get(id=replacement_id)
            
            enrolment = replacement_att.attendances.enrollment
            attendance = replacement_att.attendances

            # Not going to decrement if status is PENDING
            if replacement_att.status == "PENDING":
                enrolment.remaining_lessons -= 1
                enrolment.save()

            replacement_att.status = status
            replacement_att.save()

            attendance.has_attended = status == 'ATTENDED'
            attendance.save()


        
        except Exception as e:
            raise Exception(f"Error updating replacement lesson attendance: {str(e)}")

class EnrolmentExtensionRevertView(BaseAPIView):
    permission_classes = [IsManagerOrHigher]
    
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        try:
            branch_id = self.get_branch_id()

            enrolment_id = self.kwargs.get("enrolment_id")

            self.require_id(enrolment_id,"enrolment id")
  
            enrolment = StudentEnrolment.objects.prefetch_related(
                "extensions","payments","video_assignments"
            ).get(id=enrolment_id)

            if not enrolment:
                raise PermissionDenied("Invalid enrolment id.")
            
            if enrolment.remaining_lessons < 12:
                return Response({
                    "success": False,
                    "msg": "The student has attended extension lessons, cannot revert."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            extension_status = enrolment.extensions.last().status
            
            enrolment.extensions.last().delete()
            enrolment.video_assignments.last().delete()
            enrolment.payments.filter(enrolment_type='EXTEND').last().delete()
            
            if extension_status == 'EXTENDED':
                enrolment.remaining_lessons -= 12
                enrolment.save()

            return Response({
                "success": True,
                "msg": "Enrolment extension reverted successfully."
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "success": False,
                "msg": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
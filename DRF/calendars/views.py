from rest_framework.generics import RetrieveAPIView,DestroyAPIView,CreateAPIView,UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from accounts.permission import IsManagerOrHigher, IsPrincipalOrHigher
from api.global_customViews import (
    BaseCustomCalendarListView,BaseCustomCalendarView, GenericViewWithExtractJWTInfo,
    BaseCustomCalendarThemeLessonListView
)
from branches.models import Branch
from category.models import Category
from datetime import datetime, timedelta
from django.db import transaction

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

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        id = instance.id
        start_date  = instance.start_datetime.date()
        end_date    = instance.end_datetime.date()
        branch_id   = instance.branch_id
        
        try:
            self.perform_destroy(instance)
            self._update_calendar_theme_lesson_after_destroy(start_date,end_date,branch_id)
        except ValueError as e:
            return Response({"success": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"success": True, "message": f"Calendar {id} deleted successfully"})
    
    def _update_calendar_theme_lesson_after_destroy(self,start_date,end_date,branch_id):
        shift_days = (end_date - start_date) + timedelta(days=1)

        day_after_end_date = end_date + timedelta(days=1)

        affected_lessons = CalendarThemeLesson.objects.filter(
            branch_id=branch_id,
            lesson_date__gte=day_after_end_date,
            year=start_date.year,
        )

        updated_lessons = []
        blocked_dates = self.get_blocked_dates(start_date.year, branch_id)

        for lesson in affected_lessons:
            existing_lesson_date = datetime.strptime(str(lesson.lesson_date),"%Y-%m-%d").date()
            new_lesson_date = existing_lesson_date - shift_days
            
            while new_lesson_date in blocked_dates:
                new_lesson_date += timedelta(days=1)
            # Check if the new lesson date is beyond the year
            if new_lesson_date.year > lesson.year:
                raise ValueError(f"New lesson date {new_lesson_date} is beyond the year {lesson.year}")

            lesson.lesson_date = new_lesson_date.strftime("%Y-%m-%d")
            lesson.day = new_lesson_date.strftime("%A")
            lesson.month = new_lesson_date.month
            lesson.year = new_lesson_date.year
            
            updated_lessons.append(lesson)

        if updated_lessons:
            CalendarThemeLesson.objects.bulk_update(
                updated_lessons,
                ['lesson_date','day','month','year']
            )
    
    def get_blocked_dates(self, year, branch_id):
        """
        Get blocked dates for a specific year and branch
        """
        all_events = Calendar.objects.filter(branch_id=branch_id, year=year)
        blocked_dates = []
        for event in all_events:
            start_date = event.start_datetime.date()
            end_date = event.end_datetime.date()
            if start_date == end_date:
                blocked_dates.append(start_date)
            else:
                while start_date <= end_date:
                    blocked_dates.append(start_date)
                    start_date += timedelta(days=1)
        return blocked_dates


class CalendarCreateView(GenericViewWithExtractJWTInfo,CreateAPIView):
    serializer_class = CalendarListSerializer
    permission_classes = [IsManagerOrHigher]
    
    @transaction.atomic
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
        # self.perform_create(serializer)
        calendar_instance = serializer.save()

        try:

            if CalendarThemeLesson.objects.filter(branch_id=int(branch_id)).count() > 0:
                self._update_calendar_theme_lessons(calendar_instance)

        except ValueError as e:
            return Response({"success": False, "msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)
    
    def _update_calendar_theme_lessons(self, calendar_instance):

        start_date  = calendar_instance.start_datetime.date()
        end_date    = calendar_instance.end_datetime.date()
        branch_id   = calendar_instance.branch_id

        shift_days = (end_date - start_date) + timedelta(days=1)

        affected_lessons = CalendarThemeLesson.objects.filter(
            branch_id=branch_id,
            lesson_date__gte=start_date,
            year=start_date.year,
        )

        updated_lessons = []
        blocked_dates = self.get_blocked_dates(start_date.year, branch_id)

        for lesson in affected_lessons:
            existing_lesson_date = datetime.strptime(str(lesson.lesson_date),"%Y-%m-%d").date()
            new_lesson_date = existing_lesson_date + shift_days
            
            while new_lesson_date in blocked_dates:
                new_lesson_date += timedelta(days=1)
            # Check if the new lesson date is beyond the year
            if new_lesson_date.year > lesson.year:
                raise ValueError(f"New lesson date {new_lesson_date} is beyond the year {lesson.year}")

            lesson.lesson_date = new_lesson_date.strftime("%Y-%m-%d")
            lesson.day = new_lesson_date.strftime("%A")
            lesson.month = new_lesson_date.month
            lesson.year = new_lesson_date.year
            
            updated_lessons.append(lesson)

        if updated_lessons:
            CalendarThemeLesson.objects.bulk_update(
                updated_lessons,
                ['lesson_date','day','month','year']
            )

    def get_blocked_dates(self, year, branch_id):
        """
        Get blocked dates for a specific year and branch
        """
        all_events = Calendar.objects.filter(branch_id=branch_id, year=year)
        blocked_dates = []
        for event in all_events:
            start_date = event.start_datetime.date()
            end_date = event.end_datetime.date()
            if start_date == end_date:
                blocked_dates.append(start_date)
            else:
                while start_date <= end_date:
                    blocked_dates.append(start_date)
                    start_date += timedelta(days=1)
        return blocked_dates



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
            
class GenerateCalendarThemeLessonView(APIView):
    """
    API endpoint to generate theme lessons for a specific year and branch
    """
    permission_classes = [IsPrincipalOrHigher]  # Optional: Add authentication if needed

    def post(self, request,year):
        
        # Get branch ID from request headers
        branch_id = request.headers.get('BranchID')

        # Validate inputs
        if not branch_id:
            return Response({
                'error': 'BranchID is required in headers'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
            branch_id = int(branch_id)
        except ValueError:
            return Response({
                'error': 'Invalid year or branch ID'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            ctls = CalendarThemeLesson.objects.filter(year=year)
            if ctls.exists():
                return Response({
                    'message': f'Theme lessons already exist for year {year}'
                }, status=status.HTTP_400_BAD_REQUEST)

            categories = Category.objects.filter(year=year)
            
            if not categories.exists():
                return Response({
                    'message': f'No categories found for year {year}'
                }, status=status.HTTP_400_BAD_REQUEST)

            if categories.count() != 3:
                return Response({
                    'message': f'Expected 3 categories for year {year}, found {categories.count()}. Kindly contact admin!'
                }, status=status.HTTP_400_BAD_REQUEST)
            # Get categories and themes
            all_themes = self.get_cat_themes(categories)

            total_created = 0
            for themes in all_themes:
                # Generate theme lessons
                total_created += self.generate_theme_lessons(
                    themes=themes, 
                    year=year, 
                    branch_id=branch_id
                )

            return Response({
                "success": True,
                'data': f'Successfully generated {total_created} theme lessons'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_blocked_dates(self, year, branch_id):
        """
        Get blocked dates for a specific year and branch
        """
        all_events = Calendar.objects.filter(branch_id=branch_id, year=year)

        blocked_dates = []

        for event in all_events:
            start_date = event.start_datetime.date()
            end_date = event.end_datetime.date()

            if start_date == end_date:
                blocked_dates.append(start_date)
            else:
                while start_date <= end_date:
                    blocked_dates.append(start_date)
                    start_date += timedelta(days=1)
        
        return blocked_dates

    def get_cat_themes(self, categories):
        return [
            categories[0].themes.all(),
            categories[1].themes.all(),
            categories[2].themes.all()
        ]

    def generate_theme_lessons(self, themes, year, branch_id):
        """
        Generate theme lessons for a specific year and branch
        Ensures lessons are generated only for the specified year
        and completes 7 consecutive non-blocked days for each lesson
        """
        branch = Branch.objects.get(id=branch_id)
        blocked_dates = self.get_blocked_dates(year, branch_id)
        
        calendar_theme_lessons = []
        total_created = 0
        lesson_date = datetime(year, 1, 1).date()
        end_date = datetime(year, 12, 31).date()
        processed_themes_count = 0
        
        while lesson_date <= end_date and processed_themes_count < 12:
            for theme in themes:
                if processed_themes_count >= 12:
                    break

                for lesson in theme.theme_lessons.all():
                    # Track consecutive non-blocked days for this lesson
                    lesson_days_created = 0
                    current_lesson_date = lesson_date

                    while lesson_days_created < 7 and current_lesson_date <= end_date:
                        # Skip blocked dates
                        if current_lesson_date not in blocked_dates:
                            ctl = CalendarThemeLesson(
                                theme_lesson=lesson,
                                theme=theme,
                                branch=branch,
                                lesson_date=current_lesson_date.strftime("%Y-%m-%d"),
                                day=current_lesson_date.strftime("%A"),
                                month=current_lesson_date.month,
                                year=current_lesson_date.year,
                            )

                            calendar_theme_lessons.append(ctl)
                            lesson_days_created += 1

                            # Batch create to prevent memory issues
                            if len(calendar_theme_lessons) >= 500:
                                CalendarThemeLesson.objects.bulk_create(calendar_theme_lessons)
                                total_created += 500
                                calendar_theme_lessons = []

                        # Move to next date regardless of whether a lesson was created
                        current_lesson_date += timedelta(days=1)

                        # Break if we've gone beyond the specified year
                        if current_lesson_date.year > year:
                            break

                    # Move lesson_date forward
                    lesson_date = current_lesson_date

                    # Break out of loops if we've gone into next year
                    if lesson_date.year > year:
                        break

                # Break out of theme loop if we've gone into next year
                if lesson_date.year > year:
                    break
                
                processed_themes_count += 1

            # Break out of main loop if we've gone into next year
            if lesson_date.year > year:
                break

        # Create any remaining lessons
        if calendar_theme_lessons:
            CalendarThemeLesson.objects.bulk_create(calendar_theme_lessons)
            total_created += len(calendar_theme_lessons)

        return total_created
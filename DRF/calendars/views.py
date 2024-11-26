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
from django.core.exceptions import ValidationError

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
        """
        branch = Branch.objects.get(id=branch_id)
        blocked_dates = self.get_blocked_dates(year, branch_id)
        
        calendar_theme_lessons = []
        total_created = 0
        lesson_date = datetime(year, 1, 1).date()
        end_date = datetime(year, 12, 31).date()

        while lesson_date <= end_date:

            for theme in themes:
                for lesson in theme.theme_lessons.all():
                    # Each lesson for 7 consecutive days
                    for _ in range(7):
                        # Critical fix: Ensure we don't generate beyond the specified year
                        if lesson_date.year > year:
                            break

                        if lesson_date <= end_date and lesson_date not in blocked_dates:
                            ctl = CalendarThemeLesson(
                                theme_lesson=lesson,
                                theme=theme,
                                branch=branch,
                                lesson_date=lesson_date.strftime("%Y-%m-%d"),
                                day=lesson_date.strftime("%A"),
                                month=lesson_date.month,
                                year=lesson_date.year,
                            )

                            calendar_theme_lessons.append(ctl)

                            # Batch create to prevent memory issues
                            if len(calendar_theme_lessons) >= 500:
                                CalendarThemeLesson.objects.bulk_create(calendar_theme_lessons)
                                total_created += 500
                                calendar_theme_lessons = []

                        lesson_date += timedelta(days=1)

                        # Additional break condition to prevent generating into next year
                        if lesson_date.year > year:
                            break

                    # Break out of lesson loop if we've gone into next year
                    if lesson_date.year > year:
                        break

                # Break out of theme lessons loop if we've gone into next year
                if lesson_date.year > year:
                    break

            # Break out of theme loop if we've gone into next year
            if lesson_date.year > year:
                break

        # Create any remaining lessons
        if calendar_theme_lessons:
            CalendarThemeLesson.objects.bulk_create(calendar_theme_lessons)
            total_created += len(calendar_theme_lessons)

        return total_created
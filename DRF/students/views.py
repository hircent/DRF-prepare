from api.global_customViews import GenericViewWithExtractJWTInfo
from api.logger import Logger
from api.pagination import CustomPagination
from accounts.permission import IsTeacherOrHigher ,IsManagerOrHigher
from accounts.models import User
from branches.models import Branch ,UserBranchRole
from classes.models import StudentEnrolment
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from django.db import transaction
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from typing import List

from payments.service import PaymentService
import csv


from .models import Students
from .serializers import (
    StudentListSerializer, StudentDetailsSerializer, StudentCreateSerializer,
    StudentUpdateSerializer, StudentRemarkSerializer
)
# Create your views here.


class BasedCustomStudentsView(GenericViewWithExtractJWTInfo):

    def get_queryset(self,*args, **kwargs):
        q = self.request.query_params.get('q', None)
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)

        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            raise PermissionDenied("Branch not found.")

        query_set = branch.students.all()
        if q:
            query_set = query_set.filter(
                Q(fullname__icontains=q)  # Case-insensitive search
            )

        return query_set
            
    def get_object(self):
        student_id = self.kwargs.get("student_id")
        branch_id = self.get_branch_id()
        (is_superadmin,_) = self.branch_accessible(branch_id)

        userId = self.extract_jwt_info("user_id")

        if is_superadmin:
            # Superadmins can access any user regardless of branch
            return get_object_or_404(Students,id=student_id)
        else:
            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=User.objects.get(id=userId), branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return get_object_or_404(Students,id=student_id)

class StudentListView(BasedCustomStudentsView,generics.ListAPIView):
    serializer_class = StudentListSerializer
    permission_classes = [IsTeacherOrHigher]
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        filter = self.request.query_params.get('filter', None)

        if filter:
            queryset = queryset.filter(status=filter)

        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })
        
class StudentDetailsView(BasedCustomStudentsView,generics.RetrieveAPIView):
    serializer_class = StudentDetailsSerializer
    permission_classes = [IsTeacherOrHigher]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
class StudentCreateView(BasedCustomStudentsView,generics.CreateAPIView):
    serializer_class = StudentCreateSerializer
    permission_classes = [IsManagerOrHigher]

    def create(self, request, *args, **kwargs):
        branch_id = self.get_branch_id()
        data = request.data.copy()
        
        data['branch'] = int(branch_id)

        parent = data.get('parent')
        parent_details = data.get('parent_details')

        # If neither parent nor parent_details is provided, return error
        if not parent and not parent_details:
            return Response(
                {
                    "success": False, 
                    "message": "Either parent ID or parent details must be provided"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

class StudentUpdateView(BasedCustomStudentsView,generics.UpdateAPIView):
    serializer_class = StudentUpdateSerializer
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
    
class StudentDeleteView(BasedCustomStudentsView,generics.DestroyAPIView):
    permission_classes = [IsManagerOrHigher]

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            enrolment_ids = self._get_student_enrolments(instance.id)
            PaymentService.void_payments(
                enrolment_ids=enrolment_ids,
                description=f"Student {instance.fullname} has been deleted  at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            self.perform_destroy(instance)
            return Response({"success": True, "message": f"Student has been deleted."})
        except Exception as e:
            return Response({"success": False, "message": f"Error deleting student: {str(e)}"})
        
    def _get_student_enrolments(self,student_id:int) -> List[int]:
        return list(StudentEnrolment.objects.filter(student_id=student_id).values_list('id',flat=True))

class ExportStudentsCSV(APIView, Logger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger('export_students_csv', 'ExportStudentsCSV')

    def get(self, request):
        self.logger.info("Starting export students csv")
        
        try:
            # Try to get branchId from different possible locations
            branchId = self.request.headers.get('branchId') or \
                       self.request.GET.get('branchId') or \
                       self.request.query_params.get('branchId')
            
            self.logger.info(f"Received branchId: {branchId}")

            if not branchId:
                self.logger.error("Branch ID is required")
                return Response({"message": "Branch ID is required"}, status=status.HTTP_400_BAD_REQUEST)
                
            branch_exists = Branch.objects.filter(id=branchId).exists()
            self.logger.info(f"Branch with ID {branchId} exists: {branch_exists}")
            
            if not branch_exists:
                self.logger.error(f"Branch with ID {branchId} does not exist")
                return Response({"message": f"Branch with ID {branchId} does not exist"}, 
                                status=status.HTTP_404_NOT_FOUND)
            
            # Create the HttpResponse object with CSV header
            response = HttpResponse(
                content_type='text/csv; charset=utf-8',
                headers={
                    'Content-Disposition': f'attachment; filename="students-{datetime.now().strftime("%Y-%m-%d")}.csv"',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Accept, Content-Type, X-Requested-With, branchId',
                },
            )

            # Create CSV writer
            writer = csv.writer(response)
            
            # Write headers
            headers = [
                'Full Name',
                'Gender',
                'Date of Birth',
                'School',
                'Starting Grade',
                'Status',
                'Enrolment Date',
                'Branch',
                'Parent',
                'Email',
            ]
            writer.writerow(headers)
            self.logger.info(f"CSV headers written: {headers}")

            # Get all students with appropriate branch filtering
            # Try both string and integer comparison for branchId
            try:
                branchId_int = int(branchId)
                students = Students.objects.select_related('branch', 'parent').filter(
                    Q(branch_id=branchId) | Q(branch_id=branchId_int)
                )
            except (ValueError, TypeError):
                # If branchId can't be converted to int, just use the string
                students = Students.objects.select_related('branch', 'parent').filter(branch_id=branchId)
            
            # Log the count and first few students for debugging
            student_count = students.count()
            self.logger.info(f"Found {student_count} students for branch_id={branchId}")
            
            if student_count == 0:
                # Check if any students exist at all
                total_students = Students.objects.count()
                self.logger.info(f"Total students in database: {total_students}")
                
                # Check sample of branch IDs that do have students
                sample_branches = Students.objects.values_list('branch_id', flat=True).distinct()[:5]
                self.logger.info(f"Sample branch IDs with students: {list(sample_branches)}")
                
                # Just return empty CSV with headers
                return response
            
            # Write data
            rows_written = 0
            for student in students:
                try:
                    row = [
                        student.fullname or '',
                        student.gender or '',
                        student.dob.strftime('%Y-%m-%d') if student.dob else '',
                        student.school or '',
                        student.deemcee_starting_grade or '',
                        student.status or '',
                        student.enrolment_date.strftime('%Y-%m-%d') if student.enrolment_date else '',
                        student.branch.name if student.branch else '',
                        student.parent.username if student.parent else '',
                        student.parent.email if student.parent and hasattr(student.parent, 'email') else ''
                    ]
                    writer.writerow(row)
                    rows_written += 1
                except Exception as row_error:
                    self.logger.error(f"Error processing student {student.id if hasattr(student, 'id') else 'unknown'}: {str(row_error)}")
            
            self.logger.info(f"Successfully exported {rows_written} students")
            return response
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.logger.error(f"Export error: {str(e)}")
            self.logger.error(f"Traceback: {error_details}")
            return Response({'error': str(e)}, status=500)

class StudentRemarkView(BasedCustomStudentsView,generics.RetrieveAPIView):
    serializer_class = StudentRemarkSerializer
    permission_classes = [IsTeacherOrHigher]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
class StudentRemarkUpdateView(BasedCustomStudentsView,generics.UpdateAPIView):
    serializer_class = StudentRemarkSerializer
    permission_classes = [IsTeacherOrHigher]

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
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
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Error updating student remark: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
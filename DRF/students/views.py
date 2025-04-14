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

class ExportStudentsCSV(APIView,Logger):
    def get(self, request):
        logger = self.setup_logger('export_students_csv','ExportStudentsCSV')

        logger.info("Starting export students csv")
        logger.info(f"Request : {request}")
        try:
            branchId = self.request.headers.get('branchId')

            if not branchId:
                logger.error("Branch ID is required")
                return Response({"message": "Branch ID is required"}, status=status.HTTP_400_BAD_REQUEST)
                
            # Create the HttpResponse object with CSV header
            response = HttpResponse(
                    content_type='text/csv; charset=utf-8',
                    headers={
                        'Content-Disposition': f'attachment; filename="students-{datetime.now().strftime("%Y-%m-%d")}.csv"',
                        'Access-Control-Allow-Origin': '*',  # Or your specific frontend domain
                        'Access-Control-Allow-Methods': 'GET, OPTIONS',
                        'Access-Control-Allow-Headers': 'Accept, Content-Type, X-Requested-With, branchId',
                    },
                )

            # Create CSV writer
            writer = csv.writer(response)
            
            # Write headers
            writer.writerow([
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
            ])

            # Get all students
            students = Students.objects.select_related('branch').all()
            students = students.filter(branch_id=branchId)
            # Write data
            if students:
                for student in students:
                    writer.writerow([
                        student.fullname,
                        student.gender,
                        student.dob.strftime('%Y-%m-%d') if student.dob else '',
                        student.school,
                        student.deemcee_starting_grade,
                        student.status,
                        student.enrolment_date.strftime('%Y-%m-%d'),
                        student.branch.name,  # Assuming branch has a name field
                        student.parent.username if student.parent else '',
                        student.parent.email
                    ])

            logger.info(f"Successfully exported {len(students)} students")
            return response
        
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
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
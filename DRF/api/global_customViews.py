from accounts.models import User
from accounts.serializers import UserSerializer
from api.pagination import CustomPagination
from branches.models import Branch, UserBranchRole
from calendars.models import Calendar
from classes.models import Class,StudentEnrolment,VideoAssignment
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView


class GenericViewWithExtractJWTInfo(GenericAPIView):
    def extract_jwt_info(self,info):
        jwt_payload = self.request.auth.payload if self.request.auth else None
        
        if not jwt_payload or info not in jwt_payload:
            raise PermissionDenied("Invalid token or missing branch role information")
        
        return jwt_payload.get(info,[])
    
    def get_branch_id(self):
        branch_id = self.request.headers.get('BranchId')
        
        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        return branch_id
    
    def branch_accessible(self,branch_id):
        user_branch_roles = self.extract_jwt_info("branch_role")
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        if not is_superadmin and not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
            raise PermissionDenied("You don't have access to this branch or role.")
        
        return is_superadmin,user_branch_roles
    
class BaseCustomListAPIView(GenericViewWithExtractJWTInfo,ListAPIView):
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })

class BaseCustomListNoPaginationAPIView(GenericViewWithExtractJWTInfo,ListAPIView):

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })
    
class BaseCustomThemeListAPIView(GenericViewWithExtractJWTInfo,ListAPIView):

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })
        
class BaseCustomCalendarListView(GenericViewWithExtractJWTInfo,ListAPIView):
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })

class BaseCustomCalendarThemeLessonListView(GenericViewWithExtractJWTInfo,ListAPIView):
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })
    
    
class BaseCustomBranchSelectorListView(GenericViewWithExtractJWTInfo,ListAPIView):

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })

class BaseRoleBasedUserView(GenericViewWithExtractJWTInfo):
    serializer_class = UserSerializer

    def get_object(self):
        user_id = self.kwargs.get('pk')
        role = self.kwargs.get('role')
        branch_id = self.request.headers.get('BranchId')

        if not branch_id:
            raise PermissionDenied("Missing branch id.")

        user_branch_roles = self.extract_jwt_info("branch_role")
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        queryset = User.objects.filter(id=user_id, users__role__name=role, users__branch_id=branch_id)
        
        if not is_superadmin and not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
            raise PermissionDenied("You don't have access to this branch or role.")

        return get_object_or_404(queryset)
    
class BaseRoleBasedUserDetailsView(GenericViewWithExtractJWTInfo):
    serializer_class = UserSerializer

    def get_object(self):
        user_id = self.kwargs.get('pk')
        branch_id = self.request.headers.get('BranchId')

        if not branch_id:
            raise PermissionDenied("Missing branch id.")

        user_branch_roles = self.extract_jwt_info("branch_role")
        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        queryset = User.objects.filter(id=user_id, users__branch_id=branch_id)
        
        if not is_superadmin and not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
            raise PermissionDenied("You don't have access to this branch or role.")

        return get_object_or_404(queryset)
    
class BaseCustomBranchView(GenericViewWithExtractJWTInfo):

    def get_object(self):

        branch_id = self.kwargs.get("branch_id")

        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        user_branch_roles = self.extract_jwt_info("branch_role")
        userId = self.extract_jwt_info("user_id")

        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        if is_superadmin:
            # Superadmins can access any user regardless of branch
            return get_object_or_404(Branch,id=branch_id)
        else:
            # For non-superadmins, check if they have access to the specified branch
            if not any(ubr['branch_id'] == branch_id for ubr in user_branch_roles):
                raise PermissionDenied("You don't have access to this branch.")

            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=User.objects.get(id=userId), branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return get_object_or_404(Branch,id=branch_id)
        
class BaseCustomCalendarView(GenericViewWithExtractJWTInfo):

    def get_object(self):

        branch_id = self.request.headers.get("BranchId")
        calendar_id = self.kwargs.get("calendar_id")

        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        user_branch_roles = self.extract_jwt_info("branch_role")
        userId = self.extract_jwt_info("user_id")

        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        calendar = get_object_or_404(Calendar,id=calendar_id)
        if is_superadmin:
            
            return calendar
        else:
            # For non-superadmins, check if they have access to the specified branch
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                raise PermissionDenied("You don't have access to this branch.")

            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=User.objects.get(id=userId), branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return calendar

class BaseCustomClassView(GenericViewWithExtractJWTInfo):

    def get_object(self):

        branch_id = self.request.headers.get("BranchId")
        class_id = self.kwargs.get("class_id")

        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        user_branch_roles = self.extract_jwt_info("branch_role")
        userId = self.extract_jwt_info("user_id")

        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        clas = get_object_or_404(Class,id=class_id)
        if is_superadmin:
            
            return clas
        else:
            # For non-superadmins, check if they have access to the specified branch
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                raise PermissionDenied("You don't have access to this branch.")

            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=User.objects.get(id=userId), branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return clas
        
class BaseCustomParentView(GenericViewWithExtractJWTInfo):

    def get_object(self):

        branch_id = self.request.headers.get("BranchId")
        parent_id = self.kwargs.get("parent_id")

        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        user_branch_roles = self.extract_jwt_info("branch_role")
        userId = self.extract_jwt_info("user_id")

        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        parent = get_object_or_404(User,id=parent_id)
        if is_superadmin:
            
            return parent
        else:
            # For non-superadmins, check if they have access to the specified branch
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                raise PermissionDenied("You don't have access to this branch.")

            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=User.objects.get(id=userId), branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return parent
        
class BaseCustomEnrolmentView(GenericViewWithExtractJWTInfo):

    def get_object(self):

        branch_id = self.request.headers.get("BranchId")
        enrolment_id = self.kwargs.get("enrolment_id")

        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        user_branch_roles = self.extract_jwt_info("branch_role")
        userId = self.extract_jwt_info("user_id")

        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        enrolment = get_object_or_404(StudentEnrolment,id=enrolment_id)
        if is_superadmin:
            
            return enrolment
        else:
            # For non-superadmins, check if they have access to the specified branch
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                raise PermissionDenied("You don't have access to this branch.")

            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=User.objects.get(id=userId), branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return enrolment

class BaseVideoAssignmentView(GenericViewWithExtractJWTInfo):

    def get_object(self):

        branch_id = self.request.headers.get("BranchId")
        video_id = self.kwargs.get("video_id")

        if not branch_id:
            raise PermissionDenied("Missing branch id.")
        
        user_branch_roles = self.extract_jwt_info("branch_role")
        userId = self.extract_jwt_info("user_id")

        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        video_assignments = get_object_or_404(VideoAssignment,id=video_id)
        
        if is_superadmin:
            
            return video_assignments
        else:
            # For non-superadmins, check if they have access to the specified branch
            if not any(ubr['branch_id'] == int(branch_id) for ubr in user_branch_roles):
                raise PermissionDenied("You don't have access to this branch.")

            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=User.objects.get(id=userId), branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return video_assignments
        
class BaseAPIView(GenericViewWithExtractJWTInfo,APIView):

    def check_is_superadmin(self):
        user_branch_roles = self.extract_jwt_info("branch_role")

        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        return is_superadmin
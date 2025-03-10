from accounts.models import User
from accounts.serializers import UserSerializer
from api.pagination import CustomPagination

from branches.models import Branch, UserBranchRole

from calendars.models import Calendar
from classes.models import Class,StudentEnrolment,VideoAssignment
from certificate.models import StudentCertificate

from django.shortcuts import get_object_or_404

from payments.models import PromoCode

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
    
    def require_id(self,id,label):

        if not id:
            raise PermissionDenied(f"Missing {label}.")
        
    def require_query_param(self,param,label):

        if not param:
            raise PermissionDenied(f"Missing {label}.")
    
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
        self.require_id(user_id,"user id")

        role = self.kwargs.get('role')
        self.require_id(role,"role")

        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)

        queryset = User.objects.filter(id=user_id, users__role__name=role, users__branch_id=branch_id)

        return get_object_or_404(queryset)
    
class BaseRoleBasedUserDetailsView(GenericViewWithExtractJWTInfo):
    serializer_class = UserSerializer

    def get_object(self):
        user_id = self.kwargs.get('pk')
        self.require_id(user_id,"user id")

        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)

        queryset = User.objects.filter(id=user_id, users__branch_id=branch_id)

        return get_object_or_404(queryset)
    
class BaseCustomBranchView(GenericViewWithExtractJWTInfo):

    def get_object(self):

        branch_id = self.kwargs.get("branch_id")

        self.require_id(branch_id,"branch id")

        (is_superadmin,_) = self.branch_accessible(branch_id)

        userId = self.extract_jwt_info("user_id")

        if is_superadmin:
            # Superadmins can access any user regardless of branch
            return get_object_or_404(Branch,id=branch_id)
        else:
            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=User.objects.get(id=userId), branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return get_object_or_404(Branch,id=branch_id)
        
class BaseCustomCalendarView(GenericViewWithExtractJWTInfo):

    def get_object(self):

        calendar_id = self.kwargs.get("calendar_id")
        self.require_id(calendar_id,"calendar id")
        branch_id = self.get_branch_id()
        (is_superadmin,_) = self.branch_accessible(branch_id)
        userId = self.extract_jwt_info("user_id")

        calendar = get_object_or_404(Calendar,id=calendar_id)
        if is_superadmin:
            
            return calendar
        else:
            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=User.objects.get(id=userId), branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return calendar

class BaseCustomClassView(GenericViewWithExtractJWTInfo):

    def get_object(self):

        class_id = self.kwargs.get("class_id")
        self.require_id(class_id,"class id")

        branch_id = self.get_branch_id()
        (is_superadmin,_) = self.branch_accessible(branch_id)

        userId = self.extract_jwt_info("user_id")

        clas = get_object_or_404(Class,id=class_id)
        if is_superadmin:
            
            return clas
        else:
            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=User.objects.get(id=userId), branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return clas
        
class BaseCustomParentView(GenericViewWithExtractJWTInfo):

    def get_object(self):

        parent_id = self.kwargs.get("parent_id")

        self.require_id(parent_id,"parent id")
        
        branch_id = self.get_branch_id()
        (is_superadmin,_) = self.branch_accessible(branch_id)
        userId = self.extract_jwt_info("user_id")

        parent = get_object_or_404(User,id=parent_id)
        if is_superadmin:
            
            return parent
        else:
            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=User.objects.get(id=userId), branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return parent
        
class BaseCustomEnrolmentView(GenericViewWithExtractJWTInfo):

    def get_object(self):

        enrolment_id = self.kwargs.get("enrolment_id")

        self.require_id(enrolment_id,"enrolment id")
        
        branch_id = self.get_branch_id()
        (is_superadmin,_) = self.branch_accessible(branch_id)

        userId = self.extract_jwt_info("user_id")

        enrolment = get_object_or_404(StudentEnrolment,id=enrolment_id)
        if is_superadmin:
            
            return enrolment
        else:
            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=User.objects.get(id=userId), branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return enrolment
        
    def _check_is_payment_paid(self) -> bool:
        enrolment = self.get_object()
        return not enrolment.payments.filter(status__in=["UNPAID","PARTIALLY_PAID"]).exists()

class BaseVideoAssignmentView(GenericViewWithExtractJWTInfo):

    def get_object(self):

        video_id = self.kwargs.get("video_id")

        self.require_id(video_id,"video id")

        branch_id = self.get_branch_id()
        (is_superadmin,_) = self.branch_accessible(branch_id)

        userId = self.extract_jwt_info("user_id")

        video_assignments = get_object_or_404(VideoAssignment,id=video_id)
        
        if is_superadmin:
            
            return video_assignments
        else:
            # Check if the requested user belongs to the specified branch
            user_branch_role = UserBranchRole.objects.filter(user=User.objects.get(id=userId), branch_id=branch_id).first()
            if not user_branch_role:
                raise PermissionDenied("The requested user does not belong to the specified branch.")

            return video_assignments
        
class BasePromoCodeView(GenericViewWithExtractJWTInfo):

    def get_object(self):

        promo_code_id = self.kwargs.get("promo_code_id")

        self.require_id(promo_code_id,"promo code id")

        promo_code = get_object_or_404(PromoCode,id=promo_code_id)
        
        return promo_code
        
class BaseStudentCertificateView(GenericViewWithExtractJWTInfo):

    def get_object(self):
        cert_id = self.kwargs.get("cert_id")
        self.require_id(cert_id,"certificate id")
        return get_object_or_404(StudentCertificate,id=cert_id)

class BaseAPIView(GenericViewWithExtractJWTInfo,APIView):

    def check_is_superadmin(self):
        user_branch_roles = self.extract_jwt_info("branch_role")

        is_superadmin = any(bu['branch_role'] == 'superadmin' for bu in user_branch_roles)

        return is_superadmin
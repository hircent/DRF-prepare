from branches.models import UserBranchRole
from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        is_superadmin = UserBranchRole.objects.filter(user=request.user,role__name="superadmin").exists()
        
        return is_superadmin
        
class IsPrincipalOrHigher(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        is_principal_or_higher = UserBranchRole.objects.filter(user=request.user,role__name__in=[
            "superadmin","principal"
        ]).exists()
        
        return is_principal_or_higher
        
class IsManagerOrHigher(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        is_manager_or_higher = UserBranchRole.objects.filter(user=request.user,role__name__in=[
            "superadmin","principal","manager"
        ]).exists()
        
        return is_manager_or_higher
    
class IsTeacherOrHigher(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        is_teacher_or_higher = UserBranchRole.objects.filter(user=request.user,role__name__in=[
            "superadmin","principal","manager","teacher"
        ]).exists()
        
        return is_teacher_or_higher
    
class IsParentOrHigher(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        is_parent_or_higher = UserBranchRole.objects.filter(user=request.user,role__name__in=[
            "superadmin","principal","manager","teacher","parent"
        ]).exists()
        
        return is_parent_or_higher
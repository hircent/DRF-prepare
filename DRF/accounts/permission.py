from rest_framework.permissions import BasePermission
from branches.models import UserBranchRole

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        is_superadmin = UserBranchRole.objects.filter(user=request.user,role__name="superadmin").exists()
        
        return is_superadmin
        
        
        
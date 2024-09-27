from branches.models import UserBranchRole
from django.db.models import F
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        # Add more user data as needed
        token['full_name'] = f"{user.first_name} {user.last_name}"

        # user_branch_roles = UserBranchRole.objects.filter(user=user)
        # token['branch_ids'] = list(user_branch_roles.values_list('branch__id', flat=True).distinct())
        # token['roles'] = list(user_branch_roles.values_list('role__name', flat=True))

        user_branch_roles = UserBranchRole.objects.filter(user=user).annotate(
            branchid=F('branch__id'),
            role_name=F('role__name')
        ).values('branch_id', 'role_name')
        
        # Format branch_role as requested
        token['branch_role'] = [
            {"branch_id":item['branch_id'], "branch_role":item['role_name']} for item in user_branch_roles
        ]
        return token

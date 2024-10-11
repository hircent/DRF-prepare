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
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        # user_branch_roles = UserBranchRole.objects.filter(user=user)
        # token['branch_ids'] = list(user_branch_roles.values_list('branch__id', flat=True).distinct())
        # token['roles'] = list(user_branch_roles.values_list('role__name', flat=True))

        user_branch_roles = UserBranchRole.objects.filter(user=user).annotate(
            branchid=F('branch__id'),
            role_name=F('role__name'),
            branch_name=F('branch__name')  # Add this line to get branch name
        ).values('branch_id', 'role_name', 'branch_name')  # Include branch_name in values
        
        # Updated format to include branch_name
        token['branch_role'] = [
            {
                "branch_id": item['branch_id'],
                "branch_role": item['role_name'],
                "branch_name": item['branch_name']  # Add branch name to the output
            } for item in user_branch_roles
        ]
        return token

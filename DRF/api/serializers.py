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
        token['branch_id'] = user.branch_id
        token['roles'] = list(user.roles.values_list('name',flat=True))

        return token

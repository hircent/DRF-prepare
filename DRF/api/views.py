from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.core.cache import cache
from django.conf import settings
from .serializers import CustomTokenObtainPairSerializer, ChangePasswordSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ChangePasswordRateThrottle(UserRateThrottle):
    rate = '5/hour'  # Limit to 5 attempts per hour
    cache_format = 'change_password_throttle_%(user)s'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {
            'user': ident
        }

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    throttle_classes = [ChangePasswordRateThrottle]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        # Get attempts from cache
        cache_key = f'password_attempts_{request.user.id}'
        attempts = cache.get(cache_key, 0)

        if attempts >= 5:  # Max attempts
            return Response(
                {"msg": "Too many failed attempts. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                # Increment failed attempts
                cache.set(cache_key, attempts + 1, 3600)  # Expire in 1 hour
                return Response(
                    {"msg": "Wrong password."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            # Reset attempts on successful password change
            cache.delete(cache_key)

            return Response(
                {"msg": "Password updated successfully"},
                status=status.HTTP_200_OK
            )

        return Response({"msg":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
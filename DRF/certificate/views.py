from api.global_customViews import (
    BaseCustomListNoPaginationAPIView, BaseCustomListAPIView, BaseStudentCertificateView
)
from accounts.permission import IsSuperAdmin
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework import status

from .models import StudentCertificate
from .serializers import StudentCertificateListSerializer

# Create your views here.
class StudentCertificateListView(BaseCustomListAPIView):
    serializer_class = StudentCertificateListSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        branch_id = self.get_branch_id()
        self.branch_accessible(branch_id)

        certs = StudentCertificate.objects.filter(branch_id=branch_id)
        is_printed = self.request.query_params.get('is_printed')
        
        if is_printed and is_printed == '1':
            return certs.filter(is_printed=is_printed)

        return certs
    
class StudentCertificateUpdatePrintView(BaseStudentCertificateView,UpdateAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = StudentCertificateListSerializer

    def update(self, request, *args, **kwargs):
        cert = self.get_object()
        cert.is_printed = True
        cert.save()

        return Response(status=status.HTTP_200_OK)
from rest_framework import serializers

from .models import StudentCertificate

class StudentCertificateListSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()

    class Meta:
        model = StudentCertificate
        exclude = ('file_path','created_at','updated_at')

    def get_student(self,obj):
        return {
            "id":obj.student.id,
            "first_name":obj.student.first_name,
            "last_name":obj.student.last_name,
            "fullname":obj.student.fullname,
        }
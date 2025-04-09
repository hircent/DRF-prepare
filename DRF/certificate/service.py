from certificate.models import StudentCertificate
from datetime import datetime,date

class CertificateService:

    @staticmethod
    def generate_certificate(student_id:int, branch_id:int,start_date:str,grade:int) -> None:
        StudentCertificate.objects.create(
            student_id=student_id,
            branch_id=branch_id,
            grade=grade,
            start_date=start_date,
            end_date=datetime.today().strftime("%Y-%m-%d"),
            status='COMPLETED',
        )


    @staticmethod
    def destory_certificate(student_id:int, grade_level:int) -> None:
        if grade_level == 1:
            return
        StudentCertificate.objects.filter(student_id=student_id,grade=grade_level-1).delete()
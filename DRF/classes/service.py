from classes.models import StudentEnrolment,Class,VideoAssignment
from django.db.models import Max

class VideoAssignmentService:
    @staticmethod
    def create_video_assignments_after_advance(enrolment_instance:StudentEnrolment) -> None:

        va_arr = [
                VideoAssignment(enrolment=enrolment_instance, video_number=1),
                VideoAssignment(enrolment=enrolment_instance, video_number=2)
            ]
        VideoAssignment.objects.bulk_create(va_arr)

class EnrolmentService:
    @staticmethod
    def deactivate_enrolments(student_id:int)->None:
        enrolments = StudentEnrolment.objects.filter(student_id=student_id)

        if not enrolments.exists():
            raise Exception("No enrolment found for student id")
        
        enrolments.update(is_active=False)

    @staticmethod
    def graduate_enrolment(student_id:int)->None:
        enrolments = StudentEnrolment.objects.filter(student_id=student_id,grade__grade_level=6)

        if not enrolments.exists():
            raise Exception("No enrolment grade 6 found for this student")
        
        grade6 = enrolments.first()
        grade6.status = 'COMPLETED'
        grade6.is_active = False
        grade6.save()

    @staticmethod
    def activate_latest_enrolment(student_id:int)->None:
        enrolments = StudentEnrolment.objects.filter(student_id=student_id)
        
        if not enrolments.exists():
            raise Exception("No enrolment found for student id")
        
        max_level = enrolments.aggregate(
            max_level=Max('grade__grade_level')
        )['max_level']

        latest_enrolment = enrolments.filter(grade__grade_level=max_level).first()

        latest_enrolment.is_active = True
        latest_enrolment.status = 'IN_PROGRESS'
        latest_enrolment.save()
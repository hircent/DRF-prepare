from classes.models import StudentEnrolment,Class,VideoAssignment

class VideoAssignmentService:
    @staticmethod
    def create_video_assignments_after_advance(enrolment_instance:StudentEnrolment) -> None:

        va_arr = [
                VideoAssignment(enrolment=enrolment_instance, video_number=1),
                VideoAssignment(enrolment=enrolment_instance, video_number=2)
            ]
        VideoAssignment.objects.bulk_create(va_arr)
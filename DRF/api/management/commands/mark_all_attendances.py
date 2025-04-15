from api.baseCommand import CustomBaseCommand
from api.mixins import BlockedDatesMixin
from classes.models import ClassLesson,StudentAttendance,Class,ReplacementAttendance
from calendars.models import CalendarThemeLesson
from category.models import ThemeLesson
from branches.models import Branch
from classes.models import StudentEnrolment
from django.db import transaction
from datetime import datetime,date,timedelta
from typing import List
from django.utils.timezone import localdate

class Command(CustomBaseCommand,BlockedDatesMixin):
    help = 'Mark all attendances'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("mark_all_attendances",__name__)

    def add_arguments(self, parser):
        yesterday = localdate() - timedelta(days=1)
        parser.add_argument('--date', type=str, default=yesterday.strftime("%Y-%m-%d"), help='Date to mark attendances')
    
    @transaction.atomic
    def handle(self, *args, **kwargs):
        try:
            request_date = kwargs['date']
            date = datetime.strptime(request_date, '%Y-%m-%d').date()
            all_branches = list(Branch.objects.all().values_list('id',flat=True))

            for branch_id in all_branches:
                has_lessons = self._is_class_lesson_exists(date,branch_id)

                if not has_lessons:
                    self.stdout.write(self.style.WARNING(f"No class lessons found for date {date} and branch {branch_id},creating class lesson..."))
                    self.logger.warning(f"No class lessons found for date {date} and branch {branch_id},creating class lesson...")
                    self._create_class_lesson(date,branch_id)

                class_lessons = self._get_class_lessons(date,branch_id)

                if class_lessons:
                    for cl in class_lessons:
                        class_instance = cl.class_instance
                        enrolments = cl.class_instance.enrolments.filter(is_active=True)
                        replacement_students = cl.class_instance.replacement_attendances.filter(
                            date=date
                        ).select_related(
                            'attendances','attendances__enrollment__student','attendances__enrollment'
                        )

                        self._create_attendances(date,branch_id,enrolments,class_instance,cl.id)
                        
                        if replacement_students:
                            self._update_replacement(replacement_students,branch_id)

                        cl.status = "COMPLETED"
                        cl.save()

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during attendance marking: {str(e)}"))
            self.logger.error(f"Error during attendance marking: {str(e)}")

    def _create_class_lesson(self,date:date,branch_id:int):

        has_event = self._has_event(date,branch_id)

        if not has_event:

            class_instances = self._get_class_instance_by_day(date,branch_id)
            class_lessons_arr = []


            for ci in class_instances:
                theme_lesson = self._calendar_theme_lesson(date,branch_id,ci.name)
                
                if theme_lesson == None:
                    continue
                
                class_lesson = ClassLesson(
                    branch_id=branch_id,
                    date=date,
                    class_instance=ci,
                    theme_lesson=theme_lesson
                )
                class_lessons_arr.append(class_lesson)

            if class_lessons_arr:
                ClassLesson.objects.bulk_create(class_lessons_arr)
        else:
            self.stdout.write(self.style.WARNING(f"Is an event! Stopped create class lesson on {date} for branch {branch_id}"))
            self.logger.warning(f"Is an event! Stopped create class lesson on {date} for branch {branch_id}")

    def _get_class_instance_by_day(self,date:date,branch_id:int) -> List[Class]:
        return Class.objects.filter(branch_id=branch_id,day=date.strftime("%A"))
    
    def _calendar_theme_lesson(self,date:date,branch_id:int,category_name:str) -> ThemeLesson | None:
        ctl = CalendarThemeLesson.objects.filter(branch_id=branch_id,lesson_date=date,theme__category__name=category_name)
        if ctl.exists():
            return ctl.first().theme_lesson
        return None

    def _is_class_lesson_exists(self,date:date,branch_id:int) -> bool:
        return ClassLesson.objects.filter(branch_id=branch_id,date=date).exists()
    
    def _get_class_lessons(self,date:date,branch_id:int) -> List[ClassLesson]:
        return ClassLesson.objects.filter(branch_id=branch_id,date=date)
    
    def _create_attendances(
            self,
            date:date,branch_id:int,
            enrolments:List[StudentEnrolment],
            class_instance:Class,class_lesson_id:int
        ):
        att_arr = []
        for en in enrolments:
            enrolment_id = en.id
            is_attendance_exists = self._is_attendance_exists(date,branch_id,enrolment_id)

            if not is_attendance_exists:
                st = StudentAttendance(
                    enrollment_id=enrolment_id,
                    branch_id=branch_id,
                    class_lesson_id=class_lesson_id,
                    date=date,
                    day=date.strftime("%A"),
                    start_time=class_instance.start_time,
                    end_time=class_instance.end_time,
                    has_attended=True,
                    status="ATTENDED"
                )
                att_arr.append(st)
                en.remaining_lessons -= 1
                en.save()

        if att_arr:
            StudentAttendance.objects.bulk_create(att_arr)
            self.stdout.write(self.style.SUCCESS(f"Attendances created for date {date} and branch {branch_id}"))
            self.logger.info(f"Attendances created for date {date} and branch {branch_id}")

    def _is_attendance_exists(self,date:date,branch_id:int,enrollment_id:int) -> bool:
        return StudentAttendance.objects.filter(branch_id=branch_id,date=date,enrollment_id=enrollment_id).exists()
    
    def _update_replacement(self,replacement_students:List[ReplacementAttendance],branch_id:int) -> None:

        for replacement in replacement_students:
            replacement.status = "ATTENDED"
            replacement.attendances.enrollment.remaining_lessons -= 1
            replacement.attendances.enrollment.save()
        ReplacementAttendance.objects.bulk_update(replacement_students,["status"])
        self.stdout.write(self.style.SUCCESS(f"Replacement attendances has been updated for branch id {branch_id}"))
        self.logger.info(f"Replacement attendances has been updated for branch id {branch_id}")
        
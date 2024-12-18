from django.core.management.base import BaseCommand
from django.db.models import Q,F ,Value
from branches.models import Branch
from classes.models import Class,StudentEnrolment,ClassLesson,StudentAttendance,EnrolmentExtension
from students.models import Students


class Command(BaseCommand):
    help = 'Update all branch enrolments'

    def handle(self, *args, **kwargs):
        self.delete_enrolments()
        self.delete_enrolment_extensions()
        self.delete_attendances()

    def delete_enrolments(self):
        StudentEnrolment.objects.all().delete()
        print('enrolments deleted')

    def delete_attendances(self):
        StudentAttendance.objects.all().delete()
        print('attendances deleted')

    def delete_classes(self):
        Class.objects.all().delete()
        print('classes deleted')

    def delete_students(self):
        Students.objects.all().delete()
        print('students deleted')

    def delete_branches(self):
        Branch.objects.all().delete()
        print('branches deleted')

    def delete_enrolment_extensions(self):
        EnrolmentExtension.objects.all().delete()
        print('enrolment extensions deleted')

    def delete_class_lessons(self):
        ClassLesson.objects.all().delete()
        print('class_lessons deleted')
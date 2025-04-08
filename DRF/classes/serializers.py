from api.mixins import BlockedDatesMixin
from branches.models import Branch

from category.models import Theme
from calendars.models import Calendar
from .models import (
    Class,StudentEnrolment,ClassLesson,StudentAttendance,EnrolmentExtension, VideoAssignment,
    ReplacementAttendance
)
from category.serializers import ThemeLessonAndNameDetailsSerializer
from certificate.service import CertificateService
from classes.service import VideoAssignmentService
from category.serializers import ThemeListSerializer
from django.db.models import F,Value
from django.db import transaction
from django.utils import timezone
from datetime import timedelta ,  datetime
from feeStructure.models import Grade, Tier
from rest_framework import serializers

from payments.serializers import PaymentListSerializer
from payments.service import PaymentService
from payments.models import Payment

'''
Class Serializer
'''
class ClassListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id','branch','name','label','start_date','start_time','end_time','day']

class ClassDetailsSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = ['id','name','label','start_time','end_time','day','display_name']

    def get_display_name(self,obj:Class):
        return obj.day[:3] + ' ' + str(obj.start_time.strftime("%H:%M")) + '-' + str(obj.end_time.strftime("%H:%M"))

class RescheduleClassListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id','label']

'''
Video Assignment Serializer
'''
class VideoAssignmentListSerializer(BlockedDatesMixin,serializers.ModelSerializer):
    submit_due_date = serializers.SerializerMethodField()

    class Meta:
        model = VideoAssignment
        fields = ['id','video_number','submission_date','submit_due_date']
    
    def get_submit_due_date(self, obj):
        blockedDate = self._get_cached_blocked_dates(obj.enrolment.start_date.year, obj.enrolment.branch.id)

        current_date = obj.enrolment.start_date

        weeks_remaining = self._calculate_video_due_date_weeks(obj.video_number)

        while weeks_remaining > 0:
            current_date += timedelta(weeks=1)
            if current_date not in blockedDate:
                weeks_remaining -= 1

        return current_date.strftime("%Y-%m-%d")
    
class VideoAssignmentDetailsSerializer(BlockedDatesMixin,serializers.ModelSerializer):
    submit_due_date = serializers.SerializerMethodField()
    theme = ThemeListSerializer(read_only=True)

    class Meta:
        model = VideoAssignment
        fields = ['id','theme','video_url','video_number','submission_date','submit_due_date']

    def get_submit_due_date(self, obj):
        blockedDate = self._get_cached_blocked_dates(obj.enrolment.start_date.year, obj.enrolment.branch.id)

        current_date = obj.enrolment.start_date

        weeks_remaining = self._calculate_video_due_date_weeks(obj.video_number)

        while weeks_remaining > 0:
            current_date += timedelta(weeks=1)
            if current_date not in blockedDate:
                weeks_remaining -= 1

        return current_date.strftime("%Y-%m-%d")
    
class VideoAssignmentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoAssignment
        fields = ['id','theme','video_url','submission_date']
    
    def validate_theme(self, value):
        if value and not Theme.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid Theme ID.")
        return value
        
    def validate_video_url(self, value):
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("Invalid URL format.")
        return value

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        instance.save()
        return instance
       
'''
Student Enrolment Serializer
'''
class StudentEnrolmentListForParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrolment
        fields = [
            'id','start_date','status','remaining_lessons','is_active','freeze_lessons','grade'
        ]

class StudentEnrolmentListSerializer(serializers.ModelSerializer):
    video_assignments = VideoAssignmentListSerializer(many=True)
    student = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

    class Meta:
        model = StudentEnrolment
        fields = ['id','currency','student','start_date','grade','remaining_lessons','video_assignments','payments']

    def get_student(self, obj):
        return { "id": obj.student.id, "fullname": obj.student.fullname }
    
    def get_currency(self, obj):
        return obj.branch.country.currency
    
    def get_payments(self, obj):

        pending_payments = obj.payments.filter(status='PENDING')

        if pending_payments.exists():
            return PaymentListSerializer(pending_payments.last()).data

        return PaymentListSerializer(obj.payments.last()).data

class StudentEnrolmentListForClassSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    future_remaining_lessons = serializers.IntegerField(read_only=True)

    class Meta:
        model = StudentEnrolment
        fields = ['id', 'student','is_active','remaining_lessons','future_remaining_lessons']

    def get_student(self, obj):
        return { "id": obj.student.id, "fullname": obj.student.fullname ,"grade": obj.grade.grade_level}

class StudentEnrolmentDetailsSerializer(BlockedDatesMixin,serializers.ModelSerializer):
    end_date = serializers.SerializerMethodField()
    video_assignments = VideoAssignmentListSerializer(many=True)
    day = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    extensions = serializers.SerializerMethodField()

    class Meta:
        model = StudentEnrolment
        fields = [
            'id','start_date','end_date','day','status',
            'remaining_lessons','is_active','freeze_lessons',
            'grade','video_assignments','extensions'
        ]

    def get_extensions(self, obj):
        return {
            "total":obj.extensions.count(),
            "extension":EnrolmentExtensionDetailsSerializer(obj.extensions,many=True).data
        }
    
    def get_grade(self, obj):
        return obj.grade.grade_level
    
    def get_day(self, obj):
        return obj.classroom.day

    def get_end_date(self, obj):
        blocked_dates = self._get_cached_blocked_dates(obj.start_date.year, obj.branch.id)
    
        today = datetime.today().date()
        target_weekday = obj.start_date.weekday()
        initial_weekday = today.weekday()
        
        # Calculate initial days to reach target weekday
        days_to_add = (target_weekday - initial_weekday) % 7
        
        # Start with today's date
        current_date = today + timedelta(days=days_to_add)
        weeks_remaining = obj.remaining_lessons
        
        # Count weeks, skipping blocked dates
        while weeks_remaining > 0:
            current_date += timedelta(weeks=1)
            if current_date not in blocked_dates:
                weeks_remaining -= 1
        
        return current_date.strftime("%Y-%m-%d")

class StudentEnrolmentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentEnrolment
        fields = ['branch','grade','student','classroom','start_date']

    def validate_student(self, value):
        if value:
            enrolmentExists = StudentEnrolment.objects.filter(student=value).exists()
            if enrolmentExists:
                raise serializers.ValidationError("Student already has enrolment.Create a new enrolment is prohibited.")
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        try:
            new_enrolment = StudentEnrolment.objects.create(**validated_data)
            PaymentService.create_payment(
                enrolment=new_enrolment,
                amount=new_enrolment.grade.price,
                pre_outstanding=0,
                parent=new_enrolment.student.parent,
                enrolment_type="ENROLMENT"
            )

            VideoAssignmentService.create_video_assignments_after_advance(new_enrolment)
            return new_enrolment
        except Exception as e:
            raise serializers.ValidationError({"message": str(e), "code": "system_error"})
        
class StudentEnrolmentDetailsForUpdateViewSerializer(BlockedDatesMixin,serializers.ModelSerializer):
    tier = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()

    class Meta:
        model = StudentEnrolment
        fields = [
            'id','start_date','status','remaining_lessons',
            'is_active','freeze_lessons','grade','tier'
        ]

    def get_grade(self, obj):
        return {
            "id": obj.grade.id,
            "grade_level": obj.grade.grade_level,
            "category": obj.grade.category,
        }

    def get_tier(self, obj):
        return {
            "id": obj.grade.tier.id,
            "name": obj.grade.tier.name,
        }
        
class StudentEnrolmentUpdateSerializer(serializers.ModelSerializer):
    grade_level = serializers.IntegerField(write_only=True)
    tier = serializers.IntegerField(write_only=True)

    class Meta:
        model = StudentEnrolment
        fields = ['grade_level','is_active','status','tier']

    def validate(self, data):
        grade_level = data.get('grade_level')
        tier = data.get('tier')

        if not grade_level or not tier:
            raise serializers.ValidationError("Grade level and Tier are required.")
        
        grade = Grade.objects.filter(tier_id=tier,grade_level=grade_level)

        if not grade.exists():
            raise serializers.ValidationError("Invalid Grade.")
        
        return data
    
    def update(self, instance, validated_data):
        grade_level = validated_data.pop('grade_level')
        tier = validated_data.pop('tier')

        grade = Grade.objects.filter(tier_id=tier,grade_level=grade_level).first()
        instance = super().update(instance, validated_data)
        instance.grade = grade
        instance.save()
        return instance
    
class EnrolmentRescheduleClassSerializer(serializers.ModelSerializer):
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(),
        error_messages={
            'does_not_exist': 'Invalid classroom.',
        }
    )
    class Meta:
        model = StudentEnrolment
        fields = ['id','classroom']

    def validate_classroom(self, value):
        if not value:
            raise serializers.ValidationError("Invalid classroom provided.")
        
        if not Class.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Classroom not found.")
        return value
    
    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        instance.save()
        return instance
    
class EnrolmentAdvanceException(Exception):
    def __init__(self, message, code='advance_error'):
        self.message = message
        self.code = code
        super().__init__(self.message)
    
class EnrolmentAdvanceSerializer(serializers.ModelSerializer):
    is_early_advance = serializers.BooleanField(write_only=True)
    enrolment_id = serializers.IntegerField(write_only=True)

    EARLY_ADVANCE_LESSON_THRESHOLD = 12

    class Meta:
        model = StudentEnrolment
        fields = ['enrolment_id','classroom','start_date','grade','is_early_advance']

    def validate(self, data):
        if not data.get('enrolment_id') or not StudentEnrolment.objects.filter(id=data.get('enrolment_id')).exists():
            raise EnrolmentAdvanceException("Invalid enrolment id.")
        
        if not data.get('classroom') or not Class.objects.filter(id=data.get('classroom').id).exists():
            raise EnrolmentAdvanceException("Invalid classroom id.")
        
        if not data.get('start_date'):
            raise EnrolmentAdvanceException("Invalid start date provided.")
        
        if not data.get('grade'):
            raise EnrolmentAdvanceException("Invalid grade provided.")
        
        if 'is_early_advance' not in data:
            raise EnrolmentAdvanceException("is_early_advance field is required.")
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        enrolment_id = validated_data.get('enrolment_id')
        classroom = validated_data.get('classroom')
        start_date = validated_data.get('start_date')
        grade = validated_data.get('grade')
        is_early_advance = validated_data.get('is_early_advance')

        try:
            current_enrolment = StudentEnrolment.objects.select_related(
                'classroom','grade','branch','student'
            ).get(id=enrolment_id)
            
            self._validate_advancement_conditions(
                current_enrolment, 
                is_early_advance
            )
            
            new_enrolment = self._advance_new_enrolment(
                current_enrolment,classroom,start_date,grade
            )

            pre_outstanding = PaymentService.get_pre_outstanding(current_enrolment)

            if is_early_advance:
                balance = self._calculate_bring_forward_balance(current_enrolment)
                has_ext = EnrolmentExtension.objects.filter(enrolment=current_enrolment).exists()

                if has_ext:
                    raise serializers.ValidationError("Student has enrolment extension, cannot early advance.")
                
                PaymentService.create_payment(
                    enrolment=new_enrolment,
                    amount=new_enrolment.grade.price,
                    pre_outstanding=pre_outstanding + balance,
                    parent=current_enrolment.student.parent,
                    enrolment_type="EARLY_ADVANCE",
                    early_advance_rebate=current_enrolment.grade.price / 2
                )
            else:
                PaymentService.create_payment(
                    enrolment=new_enrolment,
                    amount=new_enrolment.grade.price,
                    pre_outstanding=pre_outstanding,
                    parent=current_enrolment.student.parent,
                    enrolment_type="ADVANCE"
                )

            CertificateService.generate_certificate(
                current_enrolment.student.id,
                current_enrolment.branch.id,
                start_date,
                current_enrolment.grade.grade_level
            )

            VideoAssignmentService.create_video_assignments_after_advance(new_enrolment)

            self._deactivate_current_enrolment(current_enrolment)
            
            return new_enrolment
        except EnrolmentAdvanceException as e:
            raise serializers.ValidationError({"message": str(e), "code": e.code})
        except Exception as e:
            raise serializers.ValidationError({"message": str(e), "code": "system_error"})
    
    def _calculate_bring_forward_balance(self,current_enrolment:StudentEnrolment) -> float:
        payment = current_enrolment.grade.price
        return payment / 2
        
    def _advance_new_enrolment(self,current_enrolment_instance:StudentEnrolment,classroom:Class,start_date:str,grade:Grade):
        current_grade_id = current_enrolment_instance.grade.tier.id
        new_grade = Grade.objects.filter(tier_id=current_grade_id,grade_level=grade.grade_level)

        if not new_grade.exists():
            raise serializers.ValidationError("Invalid grade provided")
            
        return StudentEnrolment.objects.create(
                student=current_enrolment_instance.student,
                classroom=classroom,
                start_date=start_date,
                grade_id=new_grade.first().id,
                branch=current_enrolment_instance.branch,
            )
    
    def _validate_advancement_conditions(self, current_enrolment, is_early_advance):
        if not current_enrolment.is_active:
            raise EnrolmentAdvanceException(
                "Enrollment is not active, cannot advance.",
                code="inactive_enrollment"
            )
        
        if is_early_advance and current_enrolment.remaining_lessons > self.EARLY_ADVANCE_LESSON_THRESHOLD:
            raise EnrolmentAdvanceException(
                "Enrollment has more than 12 lessons remaining, cannot advance.",
                code="too_many_lessons"
            )
        
        if not is_early_advance and current_enrolment.remaining_lessons > 0:
            raise EnrolmentAdvanceException(
                "Must finish all lessons to advance.",
                code="lessons_remaining"
            )
    
    def _deactivate_current_enrolment(self,enrolment_instance):
        enrolment_instance.is_active = False
        enrolment_instance.status = 'COMPLETED'
        enrolment_instance.save()

'''
Student Attendance Serializer
'''
class StudentAttendanceListSerializer(serializers.ModelSerializer):
    enrollment = serializers.SerializerMethodField()

    class Meta:
        model = StudentAttendance
        fields = ['id','enrollment','status']

    def get_enrollment(self, obj):
        return { 
            "id": obj.enrollment.id, 
            "student": {
                "id": obj.enrollment.student.id,
                "fullname": obj.enrollment.student.fullname,
                "grade": obj.enrollment.grade.grade_level,
            } 
        }

'''
Class Enrolment (Check For Future Lessons)
'''
class ClassEnrolmentListSerializer(serializers.ModelSerializer):
    unmarked_enrolments = serializers.SerializerMethodField()
    class_instance = serializers.SerializerMethodField()
    replacement_students = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = ['id','branch','class_instance','unmarked_enrolments','replacement_students']

    def get_unmarked_enrolments(self, obj):
        check_after_week = self.context.get('check_after_week')

        enrolments = obj.enrolments.annotate(
            future_remaining_lessons= F('remaining_lessons') - Value(check_after_week)
        ).filter(
            future_remaining_lessons__gt=0,
            is_active=True
        )

        serializer = StudentEnrolmentListForClassSerializer(enrolments, many=True)


        return serializer.data
    
    def get_class_instance(self, obj:Class):
        return {
            "name": obj.name,
            "label": obj.label,
            "start_time": obj.start_time,
            "end_time": obj.end_time,
            "day": obj.day,
            "display_name": obj.day[:3] + ' ' + str(obj.start_time.strftime("%H:%M")) + '-' + str(obj.end_time.strftime("%H:%M"))
        }
    
    def get_replacement_students(self, obj):
        date = self.context.get('date')
        replacement_students = obj.replacement_attendances.filter(
            date=datetime.strptime(date, '%Y-%m-%d').date()
        ).select_related(
            'attendances','attendances__enrollment__student','attendances__enrollment'
        )
        
        serialized_replacement_students = []
        
        for replacement in replacement_students:
            serialized_replacement_students.append({
                "id": replacement.id,
                "student":{
                    "id": replacement.attendances.enrollment.student.id,
                    "fullname": replacement.attendances.enrollment.student.fullname,
                    "grade": replacement.attendances.enrollment.grade.grade_level,
                    },
                "is_active": replacement.attendances.enrollment.is_active,
                "status": replacement.status,
                "remaining_lessons": replacement.attendances.enrollment.remaining_lessons,
                "replacement_for_lesson": replacement.attendances.date
            })
        
        return serialized_replacement_students

class ClassCreateUpdateSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        error_messages={
            'does_not_exist': 'Invalid Branch.',
        }
    )

    class Meta:
        model = Class
        fields = [
            'id',
            'branch',
            'name',
            'start_date',
            'start_time',
            'end_time',
            'day',
        ]

    def create(self, validated_data):
        # Pop the branch and category data from the validated data
        branch_data = validated_data.pop("branch", None)
        
        branch_data = Branch.objects.get(id=branch_data.id)
        # Create the class instance
        class_instance = Class.objects.create(branch=branch_data, **validated_data)

        return class_instance
    
'''
Class Lesson Serializer (Check For Attended Lessons)
'''

class ClassLessonListSerializer(serializers.ModelSerializer):
    student_attendances = serializers.SerializerMethodField()
    replacement_students = serializers.SerializerMethodField()
    class_instance = ClassDetailsSerializer(read_only=True)

    class Meta:
        model = ClassLesson
        fields = ['id','branch','class_instance',
                  'teacher','co_teacher','theme_lesson',
                  'date','status','student_attendances','replacement_students']

    def get_student_attendances(self, obj):
    # Optimize query by prefetching replacement attendance and related class instance
        attendances = obj.attendances.all().select_related(
            'enrollment__student',
            'enrollment__classroom',
            'replacement_attendances__class_instance'  # Prefetch the class instance for replacement
        )
        
        serialized_attendances = []
        
        for attendance in attendances:
            attendance_data = StudentAttendanceListSerializer(attendance).data
            
            # If status is replacement, add replacement attendance info
            if attendance.status == 'REPLACEMENT':
                try:
                    replacement = attendance.replacement_attendances
                    attendance_data['replacement_class_info'] = {
                        'id': replacement.class_instance.id,
                        'label': replacement.class_instance.label,
                        'date': replacement.date,
                        'status': replacement.status
                    }
                except StudentAttendance.replacement_attendances.RelatedObjectDoesNotExist:
                    # Handle case where there's no replacement attendance
                    attendance_data['replacement_class_info'] = None
            
            serialized_attendances.append(attendance_data)
            
        return serialized_attendances
    
    def get_replacement_students(self, obj):
        date = self.context.get('date')

        replacement_students = obj.class_instance.replacement_attendances.filter(
            date=datetime.strptime(date, '%Y-%m-%d').date()
        ).select_related(
            'attendances','attendances__enrollment__student','attendances__enrollment'
        )
        
        serialized_replacement_students = []
        
        for replacement in replacement_students:
            serialized_replacement_students.append({
                "id": replacement.id,
                "student":{
                    "id": replacement.attendances.enrollment.student.id,
                    "fullname": replacement.attendances.enrollment.student.fullname
                    },
                "is_active": replacement.attendances.enrollment.is_active,
                "status": replacement.status,
                "remaining_lessons": replacement.attendances.enrollment.remaining_lessons,
                "replacement_for_lesson": replacement.attendances.date
            })
        
        return serialized_replacement_students
    
class ClassLessonDetailsSerializer(serializers.ModelSerializer):
    theme_lesson = ThemeLessonAndNameDetailsSerializer(many=False)

    class Meta:
        model = ClassLesson
        fields = ['id','theme_lesson']
    
class TodayClassLessonSerializer(serializers.ModelSerializer):
    student_attendances = serializers.SerializerMethodField()
    class_instance = ClassDetailsSerializer(read_only=True)
    unmarked_enrolments = serializers.SerializerMethodField()
    replacement_students = serializers.SerializerMethodField()

    class Meta:
        model = ClassLesson
        fields = ['id', 'branch', 'class_instance', 
                  'teacher', 'co_teacher', 'theme_lesson', 
                  'date', 'status', 'student_attendances', 
                  'unmarked_enrolments','replacement_students']

    def get_student_attendances(self, obj):
    # Optimize query by prefetching replacement attendance and related class instance
        attendances = obj.attendances.all().select_related(
            'enrollment__student',
            'enrollment__classroom',
            'replacement_attendances__class_instance'  # Prefetch the class instance for replacement
        )
        
        serialized_attendances = []
        
        for attendance in attendances:
            attendance_data = StudentAttendanceListSerializer(attendance).data
            
            # If status is replacement, add replacement attendance info
            if attendance.status == 'REPLACEMENT':
                try:
                    replacement = attendance.replacement_attendances
                    attendance_data['replacement_class_info'] = {
                        'id': replacement.class_instance.id,
                        'label': replacement.class_instance.label,
                        'date': replacement.date,
                        'status': replacement.status
                    }
                except StudentAttendance.replacement_attendances.RelatedObjectDoesNotExist:
                    # Handle case where there's no replacement attendance
                    attendance_data['replacement_class_info'] = None
            
            serialized_attendances.append(attendance_data)
            
        return serialized_attendances
    
    def get_unmarked_enrolments(self, obj):
        # Get all active enrollments for this class
        all_enrollments = obj.class_instance.enrolments.filter(is_active=True)
        # Get IDs of students who already have attendance marked
        marked_student_ids = obj.attendances.values_list('enrollment__student__id', flat=True)
        # Filter enrollments to get only unmarked students
        unmarked_enrollments = all_enrollments.exclude(student__id__in=marked_student_ids)
        
        return StudentEnrolmentListForClassSerializer(unmarked_enrollments, many=True).data
    
    def get_replacement_students(self, obj):
        date = self.context.get('date')

        replacement_students = obj.class_instance.replacement_attendances.filter(
            date=datetime.strptime(date, '%Y-%m-%d').date()
        ).select_related(
            'attendances','attendances__enrollment__student','attendances__enrollment'
        )
        
        serialized_replacement_students = []
        
        for replacement in replacement_students:
            serialized_replacement_students.append({
                "id": replacement.id,
                "student":{
                    "id": replacement.attendances.enrollment.student.id,
                    "fullname": replacement.attendances.enrollment.student.fullname,
                    "grade": replacement.attendances.enrollment.grade.grade_level,
                    },
                "is_active": replacement.attendances.enrollment.is_active,
                "status": replacement.status,
                "remaining_lessons": replacement.attendances.enrollment.remaining_lessons,
                "replacement_for_lesson": replacement.attendances.date
            })
        
        return serialized_replacement_students

'''
Time Slot Serializer
'''
class TimeslotListSerializer(serializers.ModelSerializer):
    student_in_class = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = ['id','label','day','student_in_class']

    def get_student_in_class(self, obj):
        check_after_week = self.context.get('check_after_week')

        enrolments = obj.enrolments.annotate(
            future_remaining_lessons= F('remaining_lessons') - Value(check_after_week)
        ).filter(
            future_remaining_lessons__gt=0,
            is_active=True
        )

        return len(enrolments)

class EnrolmentLessonListSerializer(serializers.ModelSerializer):
    class_lesson = ClassLessonDetailsSerializer(read_only=True)

    class Meta:
        model = StudentAttendance
        fields = ['id','class_lesson','date','day','start_time','end_time','has_attended','status']

class EnrolmentExtensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrolment
        fields = ['id','remaining_lessons']

    def update(self, instance:StudentEnrolment, validated_data):

        enrolmentExt,created = EnrolmentExtension.objects.get_or_create(
            enrolment=instance, 
            branch=instance.branch, 
            start_date=timezone.now().date()
        )

        if created:
            instance.remaining_lessons += 12
            instance.save()

        return instance
    
class EnrolmentExtensionDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrolmentExtension
        fields = ['id','status','start_date']

class ReplacementAttendanceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplacementAttendance
        fields = ['id','attendances','class_instance','date','status']


class TestLearnSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y")
    student_name = serializers.CharField(source="student.fullname")
    class_name = serializers.CharField(source="classroom.label")
    classroom_details = ClassDetailsSerializer(source="classroom",read_only=True)

    class Meta:
        model = StudentEnrolment
        fields = [
            'id','branch','grade','student','student_name','classroom_details','class_name',
            'start_date','status','remaining_lessons','is_active','freeze_lessons',
            'created_at','updated_at'
        ]
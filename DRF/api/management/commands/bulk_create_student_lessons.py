from api.baseCommand import CustomBaseCommand
from classes.models import StudentAttendance,StudentEnrolment,ClassLesson
from branches.models import Branch
from django.db import transaction
from csv import DictReader
from datetime import datetime

class Command(CustomBaseCommand):
    help = 'Bulk import Student Lessons'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_student_attendance",__name__)
    
    def handle(self, *args, **options):
        filepath = self.get_csv_path("student_lesson.csv")
        batch_size = options['batch_size']
        start_time = datetime.now()
        
        if not filepath:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")
            
        try:
            with transaction.atomic():
                with open(filepath,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    student_attendances_arr = []
                    total_imported = 0
                    
                    for row in reader:
                        
                        try:
                            enrolment = StudentEnrolment.objects.get(id=row['enrolment_id'])
                            branch = Branch.objects.get(id=row['branch_id'])
                            class_lesson = ClassLesson.objects.get(id=row['class_lesson_id'])
                        except (Branch.DoesNotExist,ClassLesson.DoesNotExist,StudentEnrolment.DoesNotExist) as e:
                            if isinstance(e, StudentEnrolment.DoesNotExist):
                                self.logger.error(f"Student enrolment with id {row['enrolment_id']} does not exist in the database.")
                                continue
                            elif isinstance(e, ClassLesson.DoesNotExist):
                                self.logger.error(f"ClassLesson with id {row['class_lesson_id']} does not exist in the database.")
                                continue
                            else:
                                raise ImportError(f"Error while importing student_attendances: {str(e)} {row}")
                            
                        student_att = StudentAttendance(
                            id = row['id'],
                            enrollment = enrolment,
                            branch = branch,
                            class_lesson = class_lesson,
                            date = self.parse_datetime_to_date(row['start_datetime']),
                            day = self.parse_datetime_to_date(row['start_datetime']).strftime("%A"),
                            start_time = self.parse_date_to_time(row['start_datetime']),
                            end_time = self.parse_date_to_time(row['end_datetime']),
                            has_attended = self.parse_bool(row['has_attended']),
                            status = self.get_status(row['status']),
                            created_at = self.parse_datetime(row['created_at']),
                            updated_at = self.parse_datetime(row['updated_at'])
                        ) 
                        
                        student_attendances_arr.append(student_att)
                        self.stdout.write(self.style.SUCCESS(f"Student_attendance with id:{row['id']} at branch: {row['branch_id']} has appended at time {datetime.now()}"))
                        
                        if len(student_attendances_arr)>= batch_size:
                            StudentAttendance.objects.bulk_create(student_attendances_arr)
                            total_imported += len(student_attendances_arr)
                            self.logger.info(f"Imported {len(student_attendances_arr)} student_attendances. Total: {total_imported}")
                            student_attendances_arr = []
                            
                    if student_attendances_arr:
                        StudentAttendance.objects.bulk_create(student_attendances_arr)
                        total_imported += len(student_attendances_arr)
                        self.logger.info(f"Imported final batch of {len(student_attendances_arr)} student_attendances. Total: {total_imported}")
                
                self.reset_id("student_attendances")
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} student_attendances in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during student_attendance import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise

    def get_status(self,status):
        if status == '\\N':
            return 'ABSENT'
        elif status == 'COMPLETED':
            return 'ATTENDED'
        return status
    
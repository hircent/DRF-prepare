from api.baseCommand import CustomBaseCommand
from classes.models import StudentAttendance,StudentEnrolment,ClassLesson,EnrolmentExtension
from branches.models import Branch
from django.db import transaction
from csv import DictReader
from datetime import datetime

class Command(CustomBaseCommand):
    help = 'Bulk import Enrolment Extensions'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_enrolment_extensions",__name__)
    
    def handle(self, *args, **options):
        filepath = self.get_csv_path("enrolment_extensions.csv")
        batch_size = options['batch_size']
        start_time = datetime.now()
        
        if not filepath:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")
            
        try:
            with transaction.atomic():
                with open(filepath,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    extension_arr = []
                    total_imported = 0
                    
                    for row in reader:
                        
                        try:
                            enrolment = StudentEnrolment.objects.get(id=row['enrolment_id'])
                            branch = Branch.objects.get(id=row['branch_id'])
                        except (Branch.DoesNotExist,StudentEnrolment.DoesNotExist) as e:
                            if isinstance(e, StudentEnrolment.DoesNotExist):
                                self.logger.error(f"Student enrolment with id {row['enrolment_id']} does not exist in the database.")
                                continue
                            raise ImportError(f"Error while importing enrolement_extensions: {str(e)} {row}")
                            
                        student_att = EnrolmentExtension(
                            enrolment = enrolment,
                            branch = branch,
                            start_date = self.parse_date(row['start_date']),
                            created_at = self.parse_datetime(row['created_at']),
                            updated_at = self.parse_datetime(row['updated_at'])
                        ) 
                        
                        extension_arr.append(student_att)
                        enrolment.remaining_lessons += 12
                        enrolment.save()
                        self.stdout.write(self.style.SUCCESS(f"Enrolement_extensions with id:{row['id']} at branch: {row['branch_id']} has appended at time {datetime.now()}"))
                        
                        if len(extension_arr)>= batch_size:
                            EnrolmentExtension.objects.bulk_create(extension_arr)
                            total_imported += len(extension_arr)
                            self.logger.info(f"Imported {len(extension_arr)} enrolement_extensions. Total: {total_imported}")
                            extension_arr = []
                            
                    if extension_arr:
                        EnrolmentExtension.objects.bulk_create(extension_arr)
                        total_imported += len(extension_arr)
                        self.logger.info(f"Imported final batch of {len(extension_arr)} enrolement_extensions. Total: {total_imported}")
                
                self.reset_id("enrolment_extensions")
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} enrolement_extensions in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during Enrolement_extensions import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise
    
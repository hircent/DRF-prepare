from api.baseCommand import CustomBaseCommand
from certificate.models import StudentCertificate
from branches.models import Branch
from django.db import transaction
from csv import DictReader
from datetime import datetime
from students.models import Students

class Command(CustomBaseCommand):
    help = 'Bulk import Certificate'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_certificates",__name__)
    
    def handle(self, *args, **options):
        filepath = self.get_csv_path("certificate.csv")
        batch_size = options['batch_size']
        start_time = datetime.now()
        
        if not filepath:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")
            
        try:
            with transaction.atomic():
                with open(filepath,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    cert_arr = []
                    total_imported = 0

                    for row in reader:
                        try:
                            branch = Branch.objects.get(id=row['branch_id'])
                        except Branch.DoesNotExist:
                            self.logger.error(f"Branch {row['branch_id']} does not exist!")
                            raise

                        try:
                            student = Students.objects.get(id=row['student_id'])
                        except Students.DoesNotExist:
                            self.logger.error(f"Student {row['student_id']} does not exist!")
                            continue

                        cert = StudentCertificate(
                            id=row['id'],
                            student=student,
                            branch=branch,
                            grade=row['grade_id'],
                            start_date=self.parse_date(row['start_date']),
                            end_date=self.parse_date(row['end_date']),
                            status=row['status'],
                            is_printed=self.parse_bool(row['is_printed']),
                            created_at=self.parse_datetime(row['created_at']),
                            updated_at=self.parse_datetime(row['updated_at'])
                        )

                        cert_arr.append(cert)
                        self.stdout.write(self.style.SUCCESS(f"certificates with id:{row['id']} has appended at time {datetime.now()}"))

                        if len(cert_arr) >= batch_size:
                            StudentCertificate.objects.bulk_create(cert_arr)
                            total_imported += len(cert_arr)
                            self.logger.info(f"Imported {len(cert_arr)} certificates. Total: {total_imported}")
                            cert_arr = []
                    
                    if cert_arr:
                        StudentCertificate.objects.bulk_create(cert_arr)
                        total_imported += len(cert_arr)
                        self.logger.info(f"Imported final batch of {len(cert_arr)} certificates. Total: {total_imported}")
                    
                self.reset_id("certificates")
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} certificates in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during certificates import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise
    
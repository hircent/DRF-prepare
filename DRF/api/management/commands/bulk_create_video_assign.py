from api.baseCommand import CustomBaseCommand
from django.db import transaction,connection
from django.utils.timezone import make_aware
from datetime import datetime
from csv import DictReader
from classes.models import VideoAssignment,StudentEnrolment
from category.models import Theme


class Command(CustomBaseCommand):
    help = 'Import video_assigns'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_video_assigns",__name__)
    
    def handle(self, *args, **options):
        file_path = self.get_csv_path("video_assign_generated.csv")
        batch_size = options['batch_size']

        if not file_path:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")

        start_time = datetime.now()
        self.logger.info(f"Starting video_assigns import from {file_path}")

        try:
            with transaction.atomic():
                with open(file_path,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    video_assigns = []
                    total_imported = 0

                    for row in reader:
                        
                        try:
                            enrolment = StudentEnrolment.objects.get(id=row['enrolment_id'])
                            if row['theme_id']:
                                theme = Theme.objects.get(id=row['theme_id'])
                            else:
                                theme = None
                        except (StudentEnrolment.DoesNotExist , Theme.DoesNotExist) as e:
                            if isinstance(e, StudentEnrolment.DoesNotExist):
                                self.logger.error(f"Enrolment with id {row['enrolment_id']} does not exist in the database.")
                                continue
                            elif isinstance(e, Theme.DoesNotExist):
                                self.logger.error(f"Theme with id {row['theme_id']} does not exist in the database.")
                                raise ValueError(f"Theme with id {row['theme_id']} does not exist.")
    
                        va = VideoAssignment(
                            id          = row['id'],
                            enrolment   = enrolment,
                            theme       = theme,
                            video_url   = row['video_url'] if row['video_url'] else None,
                            video_number    = row['video_number'],
                            submission_date  = self.parse_datetime_to_date(row['submission_date']) if row['submission_date'] else None,
                            created_at  = self.parse_datetime(row['created_at']),
                            updated_at  = self.parse_datetime(row['updated_at']),
                        ) 
                        
                        video_assigns.append(va)
                        self.stdout.write(self.style.SUCCESS(f"Video with id:{row['id']} has appended at time {datetime.now()}"))
                        
                        if len(video_assigns)>= batch_size:
                            VideoAssignment.objects.bulk_create(video_assigns)
                            total_imported += len(video_assigns)
                            self.logger.info(f"Imported {len(video_assigns)} video_assigns. Total: {total_imported}")
                            video_assigns = []
                            
                    if video_assigns:
                        VideoAssignment.objects.bulk_create(video_assigns)
                        total_imported += len(video_assigns)
                        self.logger.info(f"Imported final batch of {len(video_assigns)} video_assigns. Total: {total_imported}")
                
                self.reset_id("video_assignments")
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} video_assigns in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during video_assign import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise

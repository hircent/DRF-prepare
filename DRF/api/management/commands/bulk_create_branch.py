from api.baseCommand import CustomBaseCommand
from branches.models import BranchAddress,Branch
from django.db import transaction
from csv import DictReader
from datetime import datetime

class Command(CustomBaseCommand):
    help = 'Bulk import branch '
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_branch",__name__)
    
    def handle(self, *args, **options):
        filepath = self.get_csv_path("branch.csv")
        batch_size = options['batch_size']
        start_time = datetime.now()
        
        if not filepath:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")
            
        try:
            with transaction.atomic():
                with open(filepath,'r') as file:
                    reader = DictReader(file)
                    branch_addr = []
                    total_imported = 0
                    
                    for row in reader:
                        ba = Branch(
                            id=row['id'],
                            branch_grade_id=row['branch_grade_id'],
                            country_id=row['country_id'],
                            name=row['name'],
                            display_name=row['display_name'],
                            business_name=row['business_name'],
                            business_reg_no=row['business_reg_no'],
                            description=row['description'],
                            operation_date=self.parse_date(row['operation_date']),
                            is_headquaters=self.parse_bool(row['is_headquarters']),
                            created_at = self.parse_datetime(row['created_at']),
                            updated_at = self.parse_datetime(row['updated_at'])
                        )    
                        
                        branch_addr.append(ba)
                        self.stdout.write(self.style.SUCCESS(f"Branch id:{row['id']} has appended at time {datetime.now()}"))
                        
                        if len(branch_addr)>= batch_size:
                            Branch.objects.bulk_create(branch_addr)
                            total_imported += len(branch_addr)
                            self.logger.info(f"Imported {len(branch_addr)} branch. Total: {total_imported}")
                            branch_addr = []
                            
                    if branch_addr:
                        Branch.objects.bulk_create(branch_addr)
                        total_imported += len(branch_addr)
                        self.logger.info(f"Imported final batch of {len(branch_addr)} branch. Total: {total_imported}")
                
                self.reset_id("branches")
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} branch in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during user profile import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise
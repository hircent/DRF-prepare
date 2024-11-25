from api.baseCommand import CustomBaseCommand
from branches.models import BranchAddress
from django.db import transaction
from csv import DictReader
from datetime import datetime

class Command(CustomBaseCommand):
    help = 'Bulk import branch addresses'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_branch_addresses",__name__)
    
    def handle(self, *args, **options):
        filepath = self.get_csv_path("branch_addresses.csv")
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
                        ba = BranchAddress(
                            branch_id = row['branch_id'],
                            address_line_1 = row['address_line_1'],
                            address_line_2 = row['address_line_2'],
                            address_line_3 = row['address_line_3'],
                            postcode = row['postcode'],
                            city = row['city'],
                            state = row['state'],
                            created_at = self.parse_datetime(row['created_at']),
                            updated_at = self.parse_datetime(row['updated_at'])
                        )    
                        
                        branch_addr.append(ba)
                        self.stdout.write(self.style.SUCCESS(f"Branch address with branch id:{row['branch_id']} has appended at time {datetime.now()}"))
                        
                        if len(branch_addr)>= batch_size:
                            BranchAddress.objects.bulk_create(branch_addr)
                            total_imported += len(branch_addr)
                            self.logger.info(f"Imported {len(branch_addr)} branch_address. Total: {total_imported}")
                            branch_addr = []
                            
                    if branch_addr:
                        BranchAddress.objects.bulk_create(branch_addr)
                        total_imported += len(branch_addr)
                        self.logger.info(f"Imported final batch of {len(branch_addr)} branch address. Total: {total_imported}")
                
                self.reset_id("branch_addresses")
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Sucessfully imported {total_imported} branch addresses in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error during user profile import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise
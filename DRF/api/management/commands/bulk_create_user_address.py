from api.baseCommand import CustomBaseCommand
from django.db import transaction
from csv import DictReader
from datetime import datetime
from accounts.models import User,UserAddress

class Command(CustomBaseCommand):
    help = 'Bulk import branch addresses'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_user_addresses",__name__)
    
    def handle(self, *args, **options):
        filepath = self.get_csv_path("user_address_generated.csv")
        batch_size = options['batch_size']
        start_time = datetime.now()
        
        if not filepath:
            self.logger.error("CSV file not found!Kindly make sure your filepath.")
            
        try:
            with transaction.atomic():
                with open(filepath,'r',encoding='utf-8') as file:
                    reader = DictReader(file)
                    user_addresses = []
                    total_imported = 0
                    
                    for row in reader:
                        
                        try:
                            # Try to get the user by the provided user_id
                            user = User.objects.get(id=row['user_id'])
                        except User.DoesNotExist:
                            # If the user doesn't exist, log the error and skip to the next row
                            self.logger.warning(f"User with id {row['user_id']} does not exist. Skipping this row.")
                            continue
                        
                        user_addresse = UserAddress(
                            user = user,
                            address_line_1 = row['address_line_1'],
                            address_line_2 = row['address_line_2'],
                            address_line_3 = row['address_line_3'],
                            postcode = row['postcode'],
                            city = row['city'],
                            state = row['state'],
                            
                            created_at = self.parse_datetime(row['created_at']) if row['created_at'] else None,
                            updated_at = self.parse_datetime(row['updated_at']) if row['updated_at'] else None,
                        )

                        user_addresses.append(user_addresse)
                        self.stdout.write(self.style.SUCCESS(f"User address with user id:{row['user_id']} has appended at time {datetime.now()}"))

                        if(len(user_addresses) >= batch_size):
                            UserAddress.objects.bulk_create(user_addresses)
                            total_imported += len(user_addresses)
                            self.logger.info(f"Imported {len(user_addresses)} user address. Total: {total_imported}")
                            user_addresses = []
                    
                    if user_addresses:
                        UserAddress.objects.bulk_create(user_addresses)
                        total_imported += len(user_addresses)
                        self.logger.info(f"Imported final batch of {len(user_addresses)} user address. Total: {total_imported}")
                
                self.reset_id("user_addresses")
                end_time = datetime.now()
                time_taken = start_time - end_time
                self.logger.info(f"Sucessfully imported {total_imported} user addresses in total.")
                self.logger.info(f"Time taken : {time_taken}")
                
        except Exception as e:
            end_time = datetime.now()
            time_taken = start_time - end_time
            self.logger.error(f"Error during user addresses import: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise
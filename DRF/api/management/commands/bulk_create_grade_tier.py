from api.baseCommand import CustomBaseCommand
from feeStructure.models import Grade,Tier
from country.models import Country
from datetime import datetime
from django.db import transaction
from feeStructure.models import Grade
from decimal import Decimal

class Command(CustomBaseCommand):
    help = 'Import grades tiers and states'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("bulk_create_grades_tiers_states",__name__)
    
    def handle(self, *args, **options):

        start_time = datetime.now()

        try:
            with transaction.atomic():
                # Create States
                countries = [
                    Country(id=1,name="Malaysia", code="MY", currency="MYR"),
                    Country(id=2,name="Australia", code="AUS", currency="AUD")
                ]
                created_countries = Country.objects.bulk_create(countries)
                
                # Get state objects
                malaysia = created_countries[0]
                australia = created_countries[1]
                
                # Create Tiers
                tiers = [
                    # Malaysia Regular Tiers
                    Tier(id=1,country=malaysia, tier_level=1,year=2023, name="Malaysia Tier 1"),
                    Tier(id=2,country=malaysia, tier_level=2,year=2023, name="Malaysia Tier 2"),
                    Tier(id=3,country=malaysia, tier_level=3,year=2023, name="Malaysia Tier 3"),
                    
                    # Malaysia Opening Tiers
                    Tier(id=4,country=malaysia, tier_level=1,year=2023, name="Malaysia Tier 1 Opening"),
                    Tier(id=5,country=malaysia, tier_level=2,year=2023, name="Malaysia Tier 2 Opening"),
                    Tier(id=6,country=malaysia, tier_level=3,year=2023, name="Malaysia Tier 3 Opening"),
                    
                    # Australia Regular Tier
                    Tier(id=7,country=australia, tier_level=1,year=2025, name="Australia Tier 1"),
                    
                    # Australia Opening Tier
                    Tier(id=8,country=australia, tier_level=1,year=2025, name="Australia Tier 1 Opening"),
                ]
                
                created_tiers = Tier.objects.bulk_create(tiers)
                
                # Define price mappings based on requirements
                pricing = {
                    # Malaysia Regular Tiers
                    "Malaysia Tier 1": {
                        "1": 1900, "2": 1900,  # Grade 1,2
                        "3": 2100, "4": 2100,  # Grade 3,4
                        "5": 2300, "6": 2300,  # Grade 5,6
                    },
                    "Malaysia Tier 2": {
                        "1": 1700, "2": 1700,
                        "3": 1900, "4": 1900,
                        "5": 2100, "6": 2100,
                    },
                    "Malaysia Tier 3": {
                        "1": 1500, "2": 1500,
                        "3": 1700, "4": 1700,
                        "5": 1900, "6": 1900,
                    },
                    
                    # Malaysia Opening Tiers
                    "Malaysia Tier 1 Opening": {
                        "1": 1700, "2": 1700,
                        "3": 1900, "4": 1900,
                        "5": 2100, "6": 2100,
                    },
                    "Malaysia Tier 2 Opening": {
                        "1": 1550, "2": 1550,
                        "3": 1750, "4": 1750,
                        "5": 1950, "6": 1950,
                    },
                    "Malaysia Tier 3 Opening": {
                        "1": 1400, "2": 1400,
                        "3": 1600, "4": 1600,
                        "5": 1800, "6": 1800,
                    },
                    
                    # Australia Regular Tier
                    "Australia Tier 1": {
                        "1": 1200, "2": 1200,
                        "3": 1300, "4": 1300,
                        "5": 1400, "6": 1400,
                    },
                    
                    # Australia Opening Tier
                    "Australia Tier 1 Opening": {
                        "1": 1080, "2": 1080,
                        "3": 1170, "4": 1170,
                        "5": 1260, "6": 1260,
                    },
                }
                
                # Define categories for grade levels
                categories = {
                    1: "KIDDO", 2: "KIDDO",
                    3: "KIDS", 4: "KIDS",
                    5: "SUPERKIDS", 6: "SUPERKIDS"
                }
                
                # Create grades
                grades = []
                
                id = 1
                for tier in created_tiers:
                    tier_price_map = pricing[tier.name]
                    
                    for grade_level in range(1, 7):
                        category = categories[grade_level]
                        price = tier_price_map[str(grade_level)]
                        
                        grades.append(Grade(
                            id=id,
                            tier=tier,
                            grade_level=grade_level,
                            category=category,
                            price=Decimal(price)
                        ))

                        id += 1
                
                Grade.objects.bulk_create(grades)
                self.stdout.write(self.style.SUCCESS(f"Grade and Tiers data created successfully!"))
                end_time = datetime.now()
                time_taken = end_time - start_time
                self.logger.info(f"Grade and Tiers data created successfully!")
                self.logger.info(f"Time taken : {time_taken}")
                
            self.reset_id("grades")
            self.reset_id("tiers")
            self.reset_id("states")
            self.reset_id("countries")
        except Exception as e:
            end_time = datetime.now()
            time_taken = end_time - start_time
            self.logger.error(f"Error creating sample data: {str(e)}")
            self.logger.error(f"Time taken : {time_taken}")
            
            raise
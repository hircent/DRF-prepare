from api.baseCommand import CustomBaseCommand
from datetime import datetime

class Command(CustomBaseCommand):

    help = 'testing function'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = self.setup_logger("testing_cronjob",__name__)

    def handle(self, *args, **kwargs):
        message = f"Cronjob started at {datetime.now()}"
        self.logger.info(message)
        print(message) 
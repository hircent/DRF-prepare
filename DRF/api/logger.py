from pathlib import Path

import logging

class Logger:
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = None

    def setup_logger(self,filename,action_name):
        logger = logging.getLogger(action_name)
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Create a file handler
        file_handler = logging.FileHandler(log_dir / f'{filename}.log')
        file_handler.setLevel(logging.INFO)
        
        # Create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add the handlers to the logger
        logger.addHandler(file_handler)
        
        return logger
from pathlib import Path

import logging

class Logger:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = None

    def setup_logger(self, filename, action_name):
        logger = logging.getLogger(f"{action_name}_{filename}")
        logger.setLevel(logging.INFO)
        
        # Check if logger already has handlers to avoid duplication
        if not logger.handlers:
            try:
                # Use absolute path or environment variable for log directory
                import os
                log_dir = os.environ.get('LOG_DIR', '/tmp/logs')
                os.makedirs(log_dir, exist_ok=True)
                
                # Create a file handler
                file_handler = logging.FileHandler(os.path.join(log_dir, f'{filename}.log'))
                file_handler.setLevel(logging.INFO)
                
                # Add console handler for immediate visibility
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                
                # Create a logging format
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(formatter)
                console_handler.setFormatter(formatter)
                
                # Add the handlers to the logger
                logger.addHandler(file_handler)
                logger.addHandler(console_handler)
                
                # Log that logger was initialized successfully
                logger.info(f"Logger {action_name}_{filename} initialized successfully")
            except Exception as e:
                # Fallback to console logging only
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)
                logger.error(f"Failed to set up file logging: {str(e)}. Using console logging only.")
        
        return logger
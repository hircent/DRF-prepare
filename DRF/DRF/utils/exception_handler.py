from rest_framework.views import exception_handler
from rest_framework.exceptions import ErrorDetail

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        # Format errors into a single message string
        formatted_errors = {}
        for field, messages in response.data.items():
            # Check if messages is a list of ErrorDetail objects
            if isinstance(messages, list):
                formatted_errors[field] = " ".join(str(msg) for msg in messages if isinstance(msg, ErrorDetail))
            else:
                formatted_errors[field] = str(messages) if isinstance(messages, ErrorDetail) else messages
        
        response.data = {
            "success":False,
            "msg": " ".join(formatted_errors.values())
        }

    return response

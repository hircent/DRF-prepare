# myapp/middleware.py
import os
from dotenv import load_dotenv
from django.http import JsonResponse

class OriginRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Load environment variables
        load_dotenv()
        
        # Check if we should allow all origins
        self.allow_all = os.getenv('ALLOW_ALL', 'False').lower() == 'true'
        
        # Get allowed origins from environment
        default_origin = "https://live-deemcee.vercel.app"
        env_origins = os.getenv('ALLOWED_ORIGINS', default_origin)
        
        # Create allowed origins list
        self.allowed_origins = [origin.strip() for origin in env_origins.split(',')]
        
        # Ensure default origin is included if not already
        if default_origin not in self.allowed_origins:
            self.allowed_origins.append(default_origin)

    def __call__(self, request):
        # If ALLOW_ALL is True, skip origin checks
        if self.allow_all:
            return self.get_response(request)
            
        # Check the Origin header
        origin = request.headers.get('Origin')
        referer = request.headers.get('Referer')
        
        # For debugging
        print(f"Request from - Origin: {origin}, Referer: {referer}")
        
        # Implement validation logic
        is_allowed = False
        
        # Internal requests (no origin/referer) are allowed
        if not origin and not referer:
            print({
                "in_allowed_origins": origin in self.allowed_origins,
                "origin": origin,
                "referer": referer
            })
        elif origin and any(origin.startswith(allowed) for allowed in self.allowed_origins):
            is_allowed = True
        # Check if referer matches allowed list
        elif referer and any(referer.startswith(allowed) for allowed in self.allowed_origins):
            is_allowed = True
        
        # Block unauthorized requests
        if not is_allowed:
            return JsonResponse({
                'error': 'Unauthorized access', 
                'message': 'This API can only be accessed from approved origins'
            }, status=403)
            
        # Process the request normally
        return self.get_response(request)
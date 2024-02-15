import logging
import json
from django.utils.deprecation import MiddlewareMixin

class LoggingMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('api_requests_logger')

    def __call__(self, request):
        excluded_paths = [
            '/api/token/',
            '/api/token/refresh/',
            '/swagger/',
            '/redoc/'
        ]

        request_body = ''
        try:
            if not any(request.path.startswith(excluded_path) for excluded_path in excluded_paths):
                request_body = request.body
                if request_body:
                    request_body = json.loads(request_body)
        except Exception as e:
            pass

        if not any(request.path.startswith(excluded_path) for excluded_path in excluded_paths):
            self.logger.info(f'Request: {request.method} {request.get_full_path()} Body: {request_body}')

        response = self.get_response(request)

        if not any(request.path.startswith(excluded_path) for excluded_path in excluded_paths):
            self.logger.info(f'Response: {response.status_code} {response.content[:1000]}')

        return response
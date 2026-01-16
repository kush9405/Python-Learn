import uuid
import logging
import time

# Get a logger instance
logger = logging.getLogger(__name__)

class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Generate a unique ID for this specific request
        request_id = str(uuid.uuid4())
        request.request_id = request_id  # Attach it to the request object

        # 2. Start timer for performance logging
        start_time = time.time()

        # 3. Log the incoming request (PRD Section 6)
        logger.info(f"REQUEST START: ID={request_id} | Path={request.path} | Method={request.method}")

        # --- CODE GOES TO THE VIEW HERE ---
        response = self.get_response(request)
        # --- CODE RETURNS FROM THE VIEW HERE ---

        # 4. Calculate duration
        duration = time.time() - start_time

        # 5. Attach ID to Response Header (PRD Section 6)
        response['X-Request-ID'] = request_id

        # 6. Log the response details
        logger.info(f"REQUEST END: ID={request_id} | Status={response.status_code} | Duration={duration:.2f}s")

        return response
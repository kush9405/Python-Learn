import uuid
import logging
import time
import threading

# Create a thread-local storage object
_thread_locals = threading.local()

class RequestIDFilter(logging.Filter):
    """
    This filter pulls the request_id from thread-local storage
    and adds it to the log record so the formatter can see it.
    """
    def filter(self, record):
        # Fallback to 'N/A' if no ID is found (e.g., for background tasks)
        record.request_id = getattr(_thread_locals, 'request_id', 'N/A')
        return True

class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Generate the ID
        request_id = str(uuid.uuid4())

        # 2. Store it in thread-locals so the filter can find it
        _thread_locals.request_id = request_id
        request.request_id = request_id

        start_time = time.time()

        # Now this logger.info will NOT crash
        logger = logging.getLogger(__name__)
        logger.info(f"REQUEST START: Path={request.path} Method={request.method}")

        response = self.get_response(request)

        duration = time.time() - start_time
        response['X-Request-ID'] = request_id

        logger.info(f"REQUEST END: Status={response.status_code} Duration={duration:.2f}s")

        # 3. Clean up after the request is done
        _thread_locals.request_id = 'N/A'

        return response
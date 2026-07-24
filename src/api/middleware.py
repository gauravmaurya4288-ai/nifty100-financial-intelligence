"""
Custom FastAPI middleware.
"""

import time
import logging

logger = logging.getLogger("api")


async def log_requests(request, call_next):
    """
    Log every request with response time.
    """

    start = time.time()

    response = await call_next(request)

    elapsed = (time.time() - start) * 1000

    logger.info(
        "%s %s %s %.2f ms",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )

    return response
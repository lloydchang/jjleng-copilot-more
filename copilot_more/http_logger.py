import json
from fastapi import Request
from copilot_more.logger import logger

async def log_request(request: Request, body: dict = None):
    """Log detailed HTTP request information"""
    logger.info("=== HTTP Request ===")
    logger.info(f"Method: {request.method}")
    logger.info(f"URL: {request.url}")
    logger.info("Headers:")
    for k, v in request.headers.items():
        # Filter out sensitive headers
        if 'auth' in k.lower() or 'key' in k.lower():
            v = '****'
        logger.info(f"  {k}: {v}")
    
    if body:
        logger.info("Body:")
        logger.info(json.dumps(body, indent=2))

def log_response_start(status_code: int, headers: dict):
    """Log HTTP response headers and status"""
    logger.info("=== HTTP Response ===")
    logger.info(f"Status: {status_code}")
    logger.info("Headers:")
    for k, v in headers.items():
        logger.info(f"  {k}: {v}")

def log_response_chunk(chunk: str):
    """Log response chunk with JSON pretty printing"""
    logger.info("=== Response Chunk ===")
    try:
        parsed = json.loads(chunk)
        logger.info(json.dumps(parsed, indent=2))
    except json.JSONDecodeError:
        logger.info(f"Raw content: {chunk}")

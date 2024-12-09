import json
import time
from fastapi import Request
from copilot_more.logger import logger

async def log_request(request: Request, body: dict = None):
    """Log detailed HTTP request information"""
    request_time = time.strftime("%Y-%m-%d %H:%M:%S")
    logger.info("\n==================== HTTP REQUEST ====================")
    logger.info(f"Timestamp: {request_time}")
    logger.info(f"Method: {request.method}")
    logger.info(f"URL: {request.url}")
    logger.info(f"Client IP: {request.client.host}")
    
    logger.info("\n----- Request Headers -----")
    for k, v in request.headers.items():
        # Filter out sensitive headers
        if any(sensitive in k.lower() for sensitive in ['auth', 'key', 'token', 'secret']):
            v = '****[REDACTED]****'
        logger.info(f"{k}: {v}")
    
    if body:
        logger.info("\n----- Request Body -----")
        try:
            formatted_body = json.dumps(body, indent=2)
            logger.info(f"\n{formatted_body}")
        except Exception as e:
            logger.info(f"Raw body: {body}")
            logger.error(f"Error formatting body: {str(e)}")

def log_response_start(status_code: int, headers: dict):
    """Log HTTP response headers and status"""
    response_time = time.strftime("%Y-%m-%d %H:%M:%S")
    logger.info("\n==================== HTTP RESPONSE ===================")
    logger.info(f"Timestamp: {response_time}")
    logger.info(f"Status Code: {status_code}")
    
    logger.info("\n----- Response Headers -----")
    for k, v in headers.items():
        if any(sensitive in k.lower() for sensitive in ['auth', 'key', 'token', 'secret']):
            v = '****[REDACTED]****'
        logger.info(f"{k}: {v}")

def log_response_chunk(chunk: str):
    """Log response chunk with JSON pretty printing"""
    logger.info("\n----- Response Chunk -----")
    try:
        parsed = json.loads(chunk)
        formatted_json = json.dumps(parsed, indent=2)
        logger.info(f"\n{formatted_json}")
    except json.JSONDecodeError:
        logger.info(f"Raw chunk content: {chunk}")

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from aiohttp import ClientSession, ClientTimeout
import json

from copilot_more.token import get_cached_copilot_token
from copilot_more.logger import logger

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


API_URL = "https://api.individual.githubcopilot.com/chat/completions"
TIMEOUT = ClientTimeout(total=300)


def preprocess_request_body(request_body: dict) -> dict:
    """
    Preprocess the request body to handle array content in messages.
    """
    if not request_body.get("messages"):
        return request_body

    processed_messages = []

    for message in request_body["messages"]:
        if not isinstance(message.get("content"), list):
            processed_messages.append(message)
            continue

        for content_item in message["content"]:
            if content_item.get("type") != "text":
                raise HTTPException(
                    400,
                    "Only text type is supported in content array"
                )

            processed_messages.append({
                "role": message["role"],
                "content": content_item["text"]
            })

    return {
        **request_body,
        "messages": processed_messages
    }


@app.post("/chat/completions")
async def proxy_chat_completions(request: Request):
    """
    Proxies chat completion requests with SSE support.
    """
    # Log request headers
    logger.info("Request Headers:")
    for k, v in request.headers.items():
        logger.info(f"{k}: {v}")
    
    request_body = await request.json()
    logger.info(f"Request Body:\n{json.dumps(request_body, indent=2)}")

    try:
        request_body = preprocess_request_body(request_body)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(400, f"Error preprocessing request: {str(e)}")

    async def stream_response():
        try:
            token = await get_cached_copilot_token()
            async with ClientSession(timeout=TIMEOUT) as session:
                async with session.post(
                    API_URL,
                    json=request_body,
                    headers={
                        "Authorization": f"Bearer {token['token']}",
                        "Content-Type": "application/json",
                        "Accept": "text/event-stream",
                        "editor-version": "vscode/1.95.3"
                    },
                ) as response:
                    # Log response details
                    logger.info(f"Response Status: {response.status}")
                    logger.info("Response Headers:")
                    for k, v in response.headers.items():
                        logger.info(f"{k}: {v}")

                    if response.status != 200:
                        error_message = await response.text()
                        logger.error(f"Response Body (Error):\n{error_message}")
                        raise HTTPException(
                            response.status,
                            f"API error: {error_message}"
                        )

                    async for chunk in response.content.iter_chunks():
                        if chunk:
                            yield chunk[0]

        # Broad exception to catch all streaming errors
        except Exception as e:  # noqa: E722  
            # Log the error and send it in the response
            error_msg = f"Error in stream_response: {str(e)}"
            logger.error(error_msg)
            yield json.dumps({"error": str(e)}).encode("utf-8")

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
    )




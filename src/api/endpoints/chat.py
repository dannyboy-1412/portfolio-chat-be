import uuid, json, logging
from typing import Annotated, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request
from pymongo.database import Database
from fastapi.responses import StreamingResponse, JSONResponse

from src.api.limiter import limiter
from src.models.chat_models import Conversation, Message, TitleInput, TelegramInputMessage
from src.services.chat_service import create_conversation, reconstruct_conversation, insert_personal_message
from src.services.ai_service import generate_completion
from src.services.telegram_bot import format_message, send_message
from src.db.base import get_db

logger = logging.getLogger(__name__)
chat_router = APIRouter()

@chat_router.post("/conversations/danny/completions", tags=["chat"])
@limiter.limit("100/minute")
async def get_personal_completions(request: Request, message: Message, db: Annotated[Database, Depends(get_db)]):
    try:
        await insert_personal_message(message, db)

        messages = reconstruct_conversation(message, db)
        stream = generate_completion(messages)
        assistant_message_id = str(uuid.uuid4())
        async def response_generator():
            full_response = ""
            yield f"metadata/&\ndata: {json.dumps({'assistant_message_id': assistant_message_id})}/&\n\n"

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield f"message/&\ndata: {json.dumps({'content': content})}/&\n\n"

            yield "[DONE]/&\n\n"
            
            assistant_message = Message(
                id=assistant_message_id,
                role="assistant",
                content=full_response,
                parent_id=message.id,
                ttl=datetime.now() + timedelta(minutes=30)
            )
            await insert_personal_message(assistant_message, db)
        
        logger.info(f"Generated completion for message {message.id}")
        return StreamingResponse(
            response_generator(),
            status_code=200,
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            },
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"Error generating completion for message {message.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

    
@chat_router.post("/conversations", tags=["chat"], response_model=Conversation)
async def create_chat(db: Annotated[Database, Depends(get_db)]):
    try:
        id = str(uuid.uuid4())
        conversation = Conversation(id=id)
        await create_conversation(
           conversation,
           db
        )
        return conversation
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Failed to create conversation"
        )
    
@chat_router.post("/conversations/{id}/title", tags=["chat"])
async def update_title(id: str, title_input: TitleInput):
    
    title = title_input.message_content
    return {"title": title}


@chat_router.post("/notifications/danny/telegram", tags=["chat"])
@limiter.limit("100/minute")
async def send_telegram_message(request: Request, message: TelegramInputMessage):
    try:
        formatted_message = format_message(message.user_message, message.assistant_message)
        message_sent = await send_message(formatted_message)

        if not message_sent:
            raise HTTPException(
                status_code=500,
                detail="Failed to send message"
            )
        logger.info(f"Message sent to telegram: {message_sent}")
        return {
            "error": False,
            "message": "Message sent successfully"
        }

    except Exception as e:
        logger.error(f"Error sending message to telegram: {e}")

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

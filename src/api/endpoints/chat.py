import uuid, json
from typing import Annotated, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from pymongo.database import Database
from fastapi.responses import StreamingResponse, JSONResponse

from src.models.chat_models import Conversation, Message, TitleInput
from src.services.chat_service import create_conversation, reconstruct_conversation, insert_personal_message
from src.services.ai_service import generate_completion
from src.db.base import get_db

chat_router = APIRouter()

@chat_router.post("/conversations/danny/completions", tags=["chat"])
async def get_personal_completions(message: Message, db: Annotated[Database, Depends(get_db)]):
    try:
        message.id = str(uuid.uuid4())
        await insert_personal_message(message, db)
        messages = reconstruct_conversation(message, db)
        stream = generate_completion(messages)
        assistant_message_id = str(uuid.uuid4())
        async def response_generator():
            full_response = ""
            yield f"event: metadata\ndata: {json.dumps({'assistant_message_id': assistant_message_id})}\n\n"

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield f"event: message\ndata: {json.dumps({'content': content})}\n\n"

            yield "event: [DONE]\n\n"
            
            assistant_message = Message(
                id=assistant_message_id,
                role="assistant",
                content=full_response,
                parent_id=message.id,
                ttl=datetime.now() + timedelta(minutes=30)
            )
            await insert_personal_message(assistant_message, db)
        
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
        print(e)
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


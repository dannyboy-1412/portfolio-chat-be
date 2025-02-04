from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


class OpenAIMessage(BaseModel):
    role: str
    content: str

class Message(OpenAIMessage):
    id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    ttl: Optional[datetime] = Field(default=None)
    parent_id: Optional[str] = Field(default=None)

class Conversation(BaseModel):
    id: str
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    model: str = Field(default="gpt-4o-mini")
    title: str = Field(default="")

class TelegramInputMessage(BaseModel):
    user_message: str
    assistant_message: Optional[str] = Field(default=None)

class TitleInput(BaseModel):

    message_content: str

from src.models.chat_models import Conversation
from src.db.base import get_db, Database
from fastapi import Depends 
from typing import Annotated, List

from src.models.chat_models import Message, OpenAIMessage

async def create_conversation(conversation: Conversation, db: Annotated[Database, Depends(get_db)]):
    """Creates a new conversation in the database.
    
    Args:
        conversation: The Conversation model to create
        
    Returns:
        The created Conversation with populated id
        
    Raises:
        pymongo.errors.PyMongoError: If database operation fails
    """
    try:
        collection = db["conversations"]
        result = collection.insert_one(conversation.model_dump())
        
        return result
        
    except Exception as e:
        # Log error here if needed
        print(e)
        raise e
    
def get_all_personal_messages(db: Database):
    try:
        collection = db["danny_messages"]
        cursor = collection.find({})  # Empty filter to get all documents
        messages = cursor.to_list(length=None)  # Convert cursor to list, None means no limit
        return messages
    except Exception as e:
        print(e)
        raise e
    

async def insert_personal_message(message: Message, db: Database):
    try:
        collection = db["danny_messages"]
        collection.insert_one(message.model_dump())
    except Exception as e:
        print(e)
        raise e

def reconstruct_conversation(message: Message, db: Database) -> List[OpenAIMessage]:
    try:
        conversation = [OpenAIMessage(role=message.role, content=message.content)]
        
        if not message.parent_id:
            print("No parent id")
            return conversation
        
        current_parent = message.parent_id
        messages = get_all_personal_messages(db)
        message_lookup = {msg["id"]: msg for msg in messages}
        while current_parent:
            if current_parent not in message_lookup:
                break  # Break if parent not found to avoid infinite loop
                
            parent_msg = message_lookup[current_parent]
            conversation.insert(0, OpenAIMessage(role=parent_msg["role"], content=parent_msg["content"]))
            current_parent = parent_msg["parent_id"]

        return conversation
    except Exception as e:
        print(f"Error reconstructing conversation: {e}")
        raise e
'''
TO DO:
- Add a function to update the conversation title
- Add a function to delete a conversation
- Add a function to get a conversation by id
- Add a function to get all conversations
- Integrate with OpenAI API
- Add the OpenAI functionality for the completions api
'''
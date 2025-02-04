import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List

from src.models.openai_response import TitleResponse
from src.models.chat_models import OpenAIMessage
# from src.services.constant_prompt import system_prompt_personal_chat
# from src.services.test_prompt import system_prompt
from src.services.system_prompt import system_prompt

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_title(conversation: str) -> TitleResponse:
    response = await client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": '''
                You are a helpful assistant.
                Your task is to summarise the conversation provided by providing a title. Your title should be no more than 5 words.
                '''
            },
            {
                "role": "user",
                "content": conversation
            }
        ],
        response_format=TitleResponse
    )
    return response.choices[0].message.content

def generate_completion(conversation: List[OpenAIMessage]) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            *(msg.model_dump() for msg in conversation)
        ],
        temperature=0.2,
        stream=True
    )
    return response



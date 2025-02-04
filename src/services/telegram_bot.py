import os
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))


def format_message(user_query: str, assistant_response: str) -> str:
    return f"User: \n{user_query}\n\nAssistant: \n{assistant_response}"

async def send_message(message: str) -> bool:
    try:
        await bot.send_message(os.getenv("CHAT_ID"), message)
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False



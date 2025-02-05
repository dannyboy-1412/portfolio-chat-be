import logging
from datetime import datetime
from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from mangum import Mangum

from src.api.limiter import limiter
from src.api.endpoints.chat import chat_router
from src.api.endpoints.resume import resume_router
from src.services.chat_service import delete_messages



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def delete_all_messages():
  logger.info("running scheduled job at %s", datetime.now())
  await delete_messages()
  logger.info("scheduled job completed at %s", datetime.now())


app = FastAPI()
# scheduler = AsyncIOScheduler()
# scheduler.add_job(delete_all_messages, 'interval', hours=2)
# scheduler.start()


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(chat_router, prefix="/chat")
api_v1_router.include_router(resume_router, prefix="/resume")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
      "http://localhost:3000",
      "https://portfolio-chat-fe-seven.vercel.app/",
      "https://portfolio-chat-fe-seven.vercel.app",
      "https://www.codestuffwdanny.com/",
      "https://www.codestuffwdanny.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],

    allow_headers=["*"],
)

@app.get("/") 
async def main_route():     
  return {"message": "Hey, It is me Goku"}

app.include_router(api_v1_router)

handler = Mangum(app)
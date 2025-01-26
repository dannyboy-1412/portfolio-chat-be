from fastapi import FastAPI, APIRouter, Depends
from src.api.endpoints.chat import chat_router
from src.api.endpoints.resume import resume_router

app = FastAPI()   
api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(chat_router, prefix="/chat")
api_v1_router.include_router(resume_router, prefix="/resume")

@app.get("/") 
async def main_route():     
  return {"message": "Hey, It is me Goku"}

app.include_router(api_v1_router)

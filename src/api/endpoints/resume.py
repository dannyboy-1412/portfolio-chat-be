from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os, logging

logger = logging.getLogger(__name__)
resume_router = APIRouter()

@resume_router.get("", 
    responses={
        200: {"description": "Resume downloaded successfully", "content": {"application/pdf": {}}},
        404: {"description": "Resume file not found"},
        500: {"description": "Internal server error"}
    },
    tags=["resume"],
    response_class=FileResponse)
async def get_resume():
    FILE_PATH = "src/static/resume.pdf"
    
    if not os.path.exists(FILE_PATH):
        raise HTTPException(status_code=404, detail="Resume file not found")
        
    try:
        logger.info(f"Serving resume file: {FILE_PATH}")
        return FileResponse(
            FILE_PATH,
            media_type="application/pdf",
            filename="daniel_resume.pdf"
        )

    except Exception as e:
        logger.error(f"Error serving resume file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to serve resume file")
from fastapi import APIRouter, UploadFile, File, HTTPException
import logging
from services.vision_service import vision_service

router = APIRouter(prefix="/api/scan", tags=["scan"])
logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
MAX_FILE_SIZE = 10 * 1024 * 1024 # 10 MB

@router.post("/ingredients")
async def scan_ingredients(file: UploadFile = File(...)):
    """
    Accepts an uploaded kitchen/food image and returns detected ingredients using Gemini Vision or Demo Provider.
    """
    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image format. Supported formats: JPG, JPEG, PNG, WEBP.")

    try:
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Image file too large. Maximum size is 10MB.")

        result = await vision_service.scan_ingredients(contents, file.filename)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing ingredient scan: {e}")
        raise HTTPException(status_code=500, detail="We couldn't identify the ingredients clearly. Try a brighter photo or add ingredients manually.")

@router.post("/meal")
async def scan_meal(file: UploadFile = File(...)):
    """
    Accepts an uploaded prepared cooked meal image and returns dish identification & estimated nutrition.
    """
    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image format. Supported formats: JPG, JPEG, PNG, WEBP.")

    try:
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Image file too large. Maximum size is 10MB.")

        result = await vision_service.scan_meal(contents, file.filename)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing meal scan: {e}")
        raise HTTPException(status_code=500, detail="We couldn't analyze the prepared meal image. Please try again or log the meal manually.")

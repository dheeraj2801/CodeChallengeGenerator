from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..ai_generator import generate_challenge_with_ai
from ..databases.db import (
    get_challenge_quota,
    create_challenge,
    create_challenge_quota,
    reset_quota_if_needed,
    get_user_challenges
)
from ..utils import authenticate_and_get_user_details
from ..databases.models import get_db
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChallengeRequest(BaseModel):
    difficulty: str
    
    class Config:
        json_schema_extra = {"example": {"difficulty": "easy"}}
        
@router.post("/generate-challenge")
async def generate_challenge(request: ChallengeRequest, request_obj: Request, db: Session = Depends(get_db)):
    try:
        logger.info("Received challenge generation request")
        user_details = authenticate_and_get_user_details(request_obj)
        user_id = user_details.get("user_id")
        logger.debug(f"User ID: {user_id}")
        
        quota = get_challenge_quota(db, user_id)
        if not quota:
            logger.info("No quota found, creating new one")
            create_challenge_quota(db, user_id)
        quota = reset_quota_if_needed(db, quota)
        logger.debug(f"Remaining quota: {quota.remaining_quota}")
        
        if quota.remaining_quota <= 0:
            logger.warning("Quota exhausted for user")
            raise HTTPException(status_code=429, detail="Quota exhausted")
        
        challenge_data = generate_challenge_with_ai(request.difficulty)
        logger.debug(f"Challenge data generated: {challenge_data}")
        
        new_challenge = create_challenge(
            db=db,
            difficulty=request.difficulty,
            created_by=user_id,
            title=challenge_data["title"],
            options=json.dumps(challenge_data["options"]),
            correct_answer_id=challenge_data["correct_answer_id"],
            explanation=challenge_data["explanation"]
        )
        
        quota.remaining_quota -= 1
        db.commit()
        logger.info(f"Challenge created with ID: {new_challenge.id}")

        return {
            "id": new_challenge.id,
            "difficulty": request.difficulty,
            "title": new_challenge.title,
            "options": json.loads(new_challenge.options),
            "correct_answer_id": new_challenge.correct_answer_id,
            "explanation": new_challenge.explanation,
            "timestamp": new_challenge.date_created.isoformat()
        }

    except Exception as e:
        logger.exception("Error generating challenge")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my-history")
async def my_history(request: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details.get("user_id")
    
    challenges = get_user_challenges(db, user_id)
    return {"challenges": challenges}

@router.get("/quota")
async def get_quota(request: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details.get("user_id")
    
    quota = get_challenge_quota(db, user_id)
    if not quota:
        return {
            "user_id": user_id,
            "quota_remaining": 0,
            "last_reset_date": datetime.now()
        }
    quota = reset_quota_if_needed(db, quota)
    return {"quota": quota}
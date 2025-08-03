from fastapi import APIRouter, HTTPException, Request, Depends
from ..databases.db import create_challenge_quota
from ..databases.models import get_db
import os
import json
from sqlalchemy.orm import Session
from svix.webhooks import Webhook

router = APIRouter()

@router.post("/clerk")
async def handle_user_created(request: Request, db: Session = Depends(get_db)):
    webhook_secret = os.getenv("CLERK_WEBHOOK_SECRET")
    
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="CLERK_WEBHOOK_SECRET not set")
    
    body = await request.body()
    payload = body.decode("utf-8")
    headers = dict(request.headers)
    
    try:
        wh = Webhook(webhook_secret)
        wh.verify(payload, headers)
        
        data = json.loads(payload)
        
        if data.get('type') != "user_created":
            return {"status": "ignored"}
        
        user_data = data.get('data', {})
        user_id = user_data.get('id')
        
        create_challenge_quota(db, user_id)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
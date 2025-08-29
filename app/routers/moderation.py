from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.db import get_db, Base, engine
from app.schemas import TextModerationIn, ModerationResultOut
from app.models.moderation import ModerationRequest, ModerationResult, NotificationLog
from app.services.llms import classify_text
from app.services.notifications import send_slack, send_email
from app.utils.hashing import sha256_hex
from app.config import settings

Base.metadata.create_all(bind=engine)

router = APIRouter()


def enforce_api_key(x_api_key: Optional[str] = Header(default=None)):
    if settings.API_KEY and x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@router.post("/text", response_model=ModerationResultOut, dependencies=[Depends(enforce_api_key)])
def moderate_text(payload: TextModerationIn, background: BackgroundTasks, db: Session = Depends(get_db)):
    # 1. Save request to DB
    content_hash = sha256_hex(payload.text)
    req = ModerationRequest(
        user_email=payload.email,
        content_type="text",
        content_hash=content_hash,
        status="processing",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    classification, confidence, reasoning, llm_raw = classify_text(payload.text)
    result = ModerationResult(
        request_id=req.id,
        classification=classification,
        confidence=confidence,
        reasoning=reasoning,
        llm_response=llm_raw,
    )
    db.add(result)

    if classification in {"toxic", "spam", "harassment"}:
        def _notify_slack(request_id: int):  # Slack notification
            ok = send_slack(
                f"[FLAGGED] {payload.email}: {classification} ({confidence:.2f})"
            )
            log = NotificationLog(
                request_id=request_id,
                channel="slack",
                status="sent" if ok else "failed",
            )
            with next(get_db()) as db2:
                db2.add(log)
                db2.commit()

    background.add_task(_notify_slack, req.id)

    def _notify_email(request_id: int):
        ok = send_email(
            to_email=payload.email,
            subject="Content Moderation Alert"
        )

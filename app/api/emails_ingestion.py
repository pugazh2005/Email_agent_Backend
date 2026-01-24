import asyncio
from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.crud.email_crud import persist_emails
from app.schemas.email_schemas import EmailCreate
from app.utils.imap_ingest import fetch_unread_emails

email_router=APIRouter(prefix="/emails")

@email_router.post("/ingest/imap")
async def receive_email(folder: str = "INBOX",db=Depends(get_db)):
    emails = await asyncio.to_thread(fetch_unread_emails, folder)
    count = await persist_emails(emails, db)
    return {
        "status": "ok",
        "folder": folder,
        "ingested": count,
    }


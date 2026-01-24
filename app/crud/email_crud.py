from sqlalchemy import select
from app.models.email_models import Email
from app.models.email_embedding import EmailEmbedding
from app.data_ingestion.utils.embed_text import embed_text
from sqlalchemy.ext.asyncio import AsyncSession


async def persist_emails(
    emails: list[dict],
    db: AsyncSession
) :
    count = 0

    for data in emails:
        email = Email(
            email_id=data["email_id"],
            sender_email=data["sender_email"],
            customer_name=data["customer_name"],
            subject=data["subject"],
            body=data["body"],
            status="received",
        )

        db.add(email)
        await db.commit()
        db.add(
            EmailEmbedding(
                email_id=email.email_id,
                embedding=embed_text(email.body),
            )
        )
        count += 1

    await db.commit()
    return count

async def fetch_email_for_run(db: AsyncSession, email_id: str):
    result = await db.execute(
        select(Email).where(
            Email.email_id == email_id,
            Email.status == "received"
        )
    )
    return result.scalar_one_or_none()


async def fetch_all_received_emails(db: AsyncSession) :
    result = await db.execute(
        select(Email).where(Email.status == "received")
    )
    return result.scalars().all()


async def fetch_needs_approval_emails(db: AsyncSession) :
    result = await db.execute(
        select(Email).where(Email.status == "needs_approval")
    )
    return result.scalars().all()


async def fetch_email_by_id(db: AsyncSession, email_id: str) :
    result = await db.execute(
        select(Email).where(Email.email_id == email_id)
    )
    return result.scalar_one_or_none()

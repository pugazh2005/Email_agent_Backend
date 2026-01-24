from imapclient import IMAPClient
import pyzmail
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.data_ingestion.utils.embed_text import embed_text
from app.models.email_embedding import EmailEmbedding
from app.models.email_models import Email
from app.models.email_embedding import EmailEmbedding

def fetch_unread_emails(folder) -> list[dict]:
    load_dotenv()

    IMAP_SERVER = os.getenv("IMAP_SERVER")
    EMAIL = os.getenv("EMAIL_ADDRESS")
    PASSWORD = os.getenv("EMAIL_PASSWORD")

    emails=[]

    with IMAPClient(IMAP_SERVER, ssl=True) as server:
        server.login(EMAIL, PASSWORD)
        server.select_folder(folder)

        messages = server.search(["UNSEEN"])

        for uid in messages:
            raw = server.fetch([uid], ["RFC822"])
            message = pyzmail.PyzMessage.factory(raw[uid][b"RFC822"])

            subject = message.get_subject()
            from_email = message.get_addresses("from")[0][1]

            if message.text_part:
                body = message.text_part.get_payload().decode(
                    message.text_part.charset or "utf-8"
                )
            else:
                body = ""

            email_id = f"email_{uid}"
            emails.append({
                "email_id":email_id,
                "sender_email": from_email,
                "customer_name": from_email.split("@")[0],
                "subject": subject,
                "body": body
            })
            server.add_flags(uid, [b"\\Seen"])

    
    return emails

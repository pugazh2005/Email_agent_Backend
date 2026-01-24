import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email_reply(to: str, subject: str, body: str):
    if not body:
        raise ValueError("Email body cannot be empty")

    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    if not EMAIL or not PASSWORD:
        raise ValueError("SMTP credentials are missing. Check .env file")

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()                 
        server.starttls()            
        server.ehlo()                 
        server.login(EMAIL, PASSWORD) 
        server.send_message(msg)      
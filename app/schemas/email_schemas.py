from typing import Literal
from pydantic import BaseModel

class EmailCreate(BaseModel):
    email_id: str
    sender_email: str
    subject:str
    body: str
    
class EmailOut(BaseModel):
    email_id: str
    sender_email: str
    intent: str | None
    urgency: str | None
    status: str

class Human_Action(BaseModel):
    action: Literal["approve", "reject", "edit"]


class ResumeAction(BaseModel):
    decision: Literal[
        "yes",
        "y",
        "approve",
        "approved",
        "no",
        "n",
        "reject",
        "rejected",
    ]
    edited_response: str | None = None
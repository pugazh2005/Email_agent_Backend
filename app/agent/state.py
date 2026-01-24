from typing import Optional,TypedDict,Literal,List

class EmailClassification(TypedDict):
    intent: Literal["question", "bug", "billing", "feature", "complex","system","personal","other"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str

class RetrievedDoc(TypedDict):
    source: str 
    content: str
    score: float

class EmailAgentState(TypedDict):
    email_id: str
    email_content: str
    sender_email: str
    customer_name:str   

    subject: Optional[str]

    classification: Optional[EmailClassification]

    search_query: Optional[str]
    retrieved_docs: Optional[List[RetrievedDoc]]

    bug_id: Optional[str]


    draft_response: Optional[str]
    final_response: Optional[str]

    has_retrieval: Optional[bool]


    needs_human_review: bool

    
    send_reply_message:Optional[str]

    
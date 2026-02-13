from app.agent.state import EmailAgentState
from app.utils.send_reply_smtp import send_email_reply
from app.core.database import async_session_maker
from app.models.response_experience import ResponseExperience
from app.data_ingestion.utils.embed_text import embed_text
from langfuse import observe

@observe()
async def send_reply(state: EmailAgentState) -> EmailAgentState:
    final_text = state["draft_response"]
    if not final_text:
        raise ValueError("No final response available to send")
    subject = state.get("subject") or ""
    subject = f"Re: {subject}".strip() if subject else "Re:"
    try:
        send_email_reply(
            to=state["sender_email"],
            subject=subject,
            body=final_text,
        )
        async with async_session_maker() as db:
            db.add(
                ResponseExperience(
                    email_intent=(state.get("classification") or {}).get("intent"),
                    urgency=(state.get("classification") or {}).get("urgency"),
                    topic=(state.get("classification") or {}).get("topic"),
                    email_embedding=embed_text(state["email_content"]),
                    response_text=final_text,
                    outcome="success",
                    feedback=None,
                )
            )
            await db.commit()
            return {
                    "final_response": final_text,
                    "send_reply_message": "Email sent successfully",
                }
    except Exception as e:
        async with async_session_maker() as db:
            db.add(
                ResponseExperience(
                    email_intent=(state.get("classification") or {}).get("intent"),
                    urgency=(state.get("classification") or {}).get("urgency"),
                    topic=(state.get("classification") or {}).get("topic"),
                    email_embedding=embed_text(state["email_content"]),
                    response_text=final_text,
                    outcome="failed",
                    feedback=str(e),
                )
            )
            await db.commit()
            raise
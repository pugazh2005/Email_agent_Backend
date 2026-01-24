from app.agent.state import EmailAgentState,EmailClassification
from app.utils.chat_llm import llm
from app.utils.prompts import build_email_classify_prompt_async
from app.utils.normalize_intent import normalize_intent

from langfuse import observe

@observe()
async def classify_email(state:EmailAgentState) -> EmailAgentState:
    structured_llm=llm.with_structured_output(EmailClassification)
    classification_prompt=await build_email_classify_prompt_async(state['email_content'],state['sender_email'])
    result=await structured_llm.ainvoke(classification_prompt)
    normalized_intent = normalize_intent(
        result["intent"],
        state["sender_email"]
    )
    result["intent"] = normalized_intent
    return {
        "classification": result,
        "search_query": f"{result['intent']} {result['topic']}"
    }
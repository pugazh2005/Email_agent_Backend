from langfuse import get_client
import asyncio

langfuse=get_client()

def build_email_classify_prompt(email_context:str,sender_email:str):
    classification_prompt=langfuse.get_prompt("email_agent/classify_email_prompt")
    return classification_prompt.compile(
        email_context=email_context,
        sender_email=sender_email
    )
async def build_email_classify_prompt_async(email_context:str,sender_email:str):
    return await asyncio.to_thread(build_email_classify_prompt,email_context,sender_email)

def build_write_response_prompt(email_content:str,customer_name:str,intent:str,urgency:str,docs:str):
    write_response=langfuse.get_prompt("email_agent/write_response_prompt")
    return write_response.compile(
        email_content=email_content,
        customer_name=customer_name,
        intent=intent,
        urgency=urgency,
        docs=docs
    )

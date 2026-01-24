ALLOWED_INTENTS = {
    "question",
    "bug",
    "billing",
    "feature",
    "complex",
    "system",
    "personal",
    "other",
}

SYSTEM_SENDERS = (
    "no-reply@",
    "noreply@",
    "accounts.google.com",
)

def normalize_intent(raw_intent: str, sender: str) -> str:
    raw_intent = raw_intent.lower().strip()

   
    if sender.lower().startswith(SYSTEM_SENDERS):
        return "system"

    if raw_intent in ALLOWED_INTENTS:
        return raw_intent

    if raw_intent in {"notification", "alert", "security"}:
        return "system"

    return "other"

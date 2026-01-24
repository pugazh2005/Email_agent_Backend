# Agentic Email Support System

LangGraph-powered email agent that ingests knowledge PDFs, classifies incoming emails, retrieves relevant context (RAG), drafts responses, supports human-in-the-loop review, and sends replies. Postgres-based checkpointing enables resumable runs after interrupts.

## Features
- IMAP ingestion; SMTP replies.
- LLM-based intent/urgency/topic/summary classification.
- RAG over ingested PDFs and successful past replies.
- Bug ticket auto-creation for bug intents.
- Human-in-the-loop with LangGraph interrupts and resume.
- Async FastAPI service; Postgres + pgvector for storage.

## Architecture Overview
- API (FastAPI routers):
	- Knowledge upload: app/api/knowledge_ingestion.py
	- Email ingest: app/api/emails_ingestion.py
	- Agent run/resume: app/api/agent_endpoints.py
- Agent graph (LangGraph):
	- Nodes: read_email → classify_email → persist_classification → retrieve_docs → (bug_tracking | write_response) → (human_review) → send_reply
	- Defined in app/agent/graph/agent_graph.py; instantiated with Postgres checkpointer in app/main.py; shared via app/agent/graph/graph_holder.py.
- Data ingestion graph:
	- parse_pdf → embed_and_store → update_state
	- Defined in app/data_ingestion/graph/data_ingestion_graph.py.
- Persistence:
	- Postgres models in app/models/*
	- pgvector for embeddings (knowledge_base, email_embeddings, response_experience)
	- LangGraph Postgres checkpointer for resumable workflows.

## Prerequisites
- Python 3.12+
- Postgres with pgvector extension enabled.
- (Windows) Use selector event loop for psycopg async in helper scripts.

## Setup
1) Install dependencies
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

2) Environment (.env, gitignored)
```
EMAIL_ADDRESS=...
EMAIL_PASSWORD=...
IMAP_SERVER=...
SMTP_SERVER=...
SMTP_PORT=587
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
CHECKPOINTER_URL=postgresql://user:pass@host:5432/db
GROQ_API_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_BASE_URL=...
```

3) Database
- Ensure pgvector extension is installed.
- App tables create on first use via SQLAlchemy models.
- LangGraph checkpoint tables: run the helper script once (below).

### Initialize LangGraph checkpoint tables (Postgres)
python_ex.py runs AsyncPostgresSaver.setup() (Windows-safe loop policy):
```bash
python python_ex.py
```
Creates:
- checkpoints
- checkpoint_writes
- checkpoint_blobs
- checkpoint_migrations

If schema mismatch occurs, drop these tables and rerun the script.

## Run the Service
```bash
. .venv/Scripts/activate
uvicorn app.main:app --reload
```
app/main.py builds the email graph with the Postgres checkpointer during lifespan startup.

## API Endpoints
- POST /knowledge/upload — upload a PDF to ingest into KB.
- POST /emails/ingest/imap — fetch unread emails from IMAP into the DB.
- POST /agent/run?email_id=... — process a single email (email_id is the thread_id).
- POST /agent/run-all — process all emails with status received.
- GET /agent/emails/needs-approval — list emails awaiting human review.
- POST /agent/resume/{email_id}?thread_id=... — resume an interrupted run with decision data.

## Human-in-the-Loop Flow
- High/critical urgency or complex/personal intents trigger human_review interrupt.
- Resume with the same thread_id (defaults to email_id) and a decision:
	- approve → send draft/final
	- edit → send edited response
	- reject → end without sending
- Checkpointer restores full state so the graph does not restart from read_email.

## Data Ingestion
- POST /knowledge/upload with a PDF:
	- parse_pdf: chunk via PyMuPDF + RecursiveCharacterTextSplitter
	- embed_and_store: embed chunks, store in knowledge_base
	- update_state: sets system_state.kb_ready = true
- Retrieval (retrieve_docs) pulls from knowledge_base and successful response_experience when kb_ready is true and intent is not system/personal/other.

## Persistence Models (app/models)
- emails, email_embeddings, knowledge_base, response_experience, bugs, system_state
- response_experience logs successful/failed replies for retrieval and analysis.

## Key Files
- API: app/api/agent_endpoints.py, app/api/knowledge_ingestion.py, app/api/emails_ingestion.py
- Agent graph: app/agent/graph/agent_graph.py; runner: app/agent/runner.py; nodes in app/agent/nodes/*
- Data ingestion graph: app/data_ingestion/graph/data_ingestion_graph.py
- Utils (LLM, embeddings, prompts, email IO): app/utils/*
- Checkpointer wiring: app/main.py
- Helper script to create checkpoint tables: python_ex.py

## Troubleshooting
- relation checkpoints does not exist or missing columns: drop existing checkpoint tables, rerun python python_ex.py, then restart the app.
- email_content missing from state on resume: ensure thread_id in /agent/resume matches the original run’s email_id and a checkpoint exists for that thread.
- Windows psycopg async issues: use the selector event loop (already handled in python_ex.py).

## Deployment Notes
- Ensure Postgres user has DDL rights for checkpoint setup.
- Keep .env out of Git (already in .gitignore).
- For multi-worker Uvicorn/Gunicorn, point all workers to the same CHECKPOINTER_URL; the Postgres checkpointer is worker-safe.

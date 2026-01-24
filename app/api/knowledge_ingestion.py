import tempfile
from fastapi import APIRouter, Depends, File, UploadFile
from app.data_ingestion.runner import run_ingestion_graph

from app.core.database import get_db

know_router=APIRouter(prefix="/knowledge",tags=["Knowledge Base"])

@know_router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.file.read())
        temp_path = tmp.name
    return await run_ingestion_graph(
        file_path=temp_path,
        file_name=file.filename,
        db=db
    )

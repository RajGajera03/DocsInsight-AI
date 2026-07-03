import os
import shutil
import fitz  # PyMuPDF
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.config import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.auth.router import get_current_user
from app.ai.pipeline import process_pdf_and_store, delete_document_from_vectorstore

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{current_user.id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract number of pages
    try:
        doc = fitz.open(file_path)
        num_pages = len(doc)
        doc.close()
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Invalid PDF file")

    # Create DB entry
    db_document = Document(
        user_id=current_user.id,
        filename=file.filename,
        num_pages=num_pages,
        file_path=file_path
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Trigger background processing for Vector DB
    background_tasks.add_task(process_pdf_and_store, file_path, db_document.id)

    return db_document

@router.get("/", response_model=List[DocumentResponse])
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return documents

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id, 
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete the physical file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # Delete from Vector DB
    delete_document_from_vectorstore(str(document.id))

    # Delete DB entry
    db.delete(document)
    db.commit()
    
    return None

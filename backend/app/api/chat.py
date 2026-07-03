from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.config import get_db
from app.models.chat import ChatSession, Message
from app.models.user import User
from app.schemas.chat import ChatSessionCreate, ChatSessionResponse, ChatRequest, MessageResponse
from app.auth.router import get_current_user
from app.ai.pipeline import ask_question

router = APIRouter()

@router.post("/sessions", response_model=ChatSessionResponse)
def create_chat_session(
    session_in: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_session = ChatSession(
        user_id=current_user.id,
        document_id=session_in.document_id
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/history", response_model=List[ChatSessionResponse])
def get_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).all()
    return sessions

@router.post("/", response_model=MessageResponse)
def chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == chat_request.session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Save user message
    user_msg = Message(
        session_id=session.id,
        role="user",
        content=chat_request.question
    )
    db.add(user_msg)
    db.commit()

    # Get answer from LangGraph
    document_id_str = str(chat_request.document_id) if chat_request.document_id else None
    
    # We could theoretically pull conversation history here and pass it to graph
    # For now, it answers based strictly on context
    try:
        answer_text = ask_question(chat_request.question, document_id_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Save assistant message
    ai_msg = Message(
        session_id=session.id,
        role="assistant",
        content=answer_text
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return ai_msg

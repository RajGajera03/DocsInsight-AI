from fastapi import APIRouter
from app.auth.router import router as auth_router
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.database.config import engine, Base
from app.models.user import User
from app.models.document import Document
from app.models.chat import ChatSession, Message

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI PDF Q&A Assistant API",
    description="Backend API for the PDF Q&A application",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}

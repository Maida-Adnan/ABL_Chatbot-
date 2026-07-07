import uuid
import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.rag_pipeline import answer_question
from core.memory import clear_history

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    session_id: str = ""  # optional — frontend generates this


class ChatResponse(BaseModel):
    answer: str
    session_id: str


class ResetRequest(BaseModel):
    session_id: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # If no session_id provided, generate one (first message in a new conversation)
    session_id = request.session_id or str(uuid.uuid4())

    try:
        answer = answer_question(request.question, session_id)
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=503, detail="Sorry, I'm having trouble answering right now. Please try again.")

    return ChatResponse(answer=answer, session_id=session_id)


@router.post("/chat/reset")
def reset_chat(request: ResetRequest):
    """Clears conversation history for a session."""
    clear_history(request.session_id)
    return {"message": "Conversation history cleared."}
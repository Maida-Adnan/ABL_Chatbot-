# routers/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.rag_pipeline import answer_question

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    answer = answer_question(request.question)
    return ChatResponse(answer=answer)
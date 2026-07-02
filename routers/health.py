# routers/health.py
from fastapi import APIRouter
import ollama
from core.vectorstore import get_collection_count

router = APIRouter()


@router.get("/health")
def health_check():
    status = {"ollama": "unknown", "chromadb": "unknown"}

    try:
        ollama.list()
        status["ollama"] = "ok"
    except Exception:
        status["ollama"] = "unreachable"

    try:
        count = get_collection_count()
        status["chromadb"] = f"ok ({count} chunks)"
    except Exception:
        status["chromadb"] = "unreachable"

    return status
# core/rag_pipeline.py
from core.retriever import retrieve
from core.prompt_builder import build_prompt
from core.ollama_client import ask_model

DISTANCE_THRESHOLD = 400

GREETINGS = {"hi", "hello", "hey", "salam", "assalam", "good morning", "good evening", "good afternoon"}


def is_greeting(question: str) -> bool:
    return question.strip().lower() in GREETINGS


def answer_question(question: str, top_k: int = 3) -> str:
    """
    Full RAG flow: retrieve relevant chunks, check if they're actually
    relevant enough, build a prompt, and ask the model -- or return
    a fallback message if nothing relevant was found.
    """
    if not question or not question.strip():
        return "Please enter a question so I can help you."

    if is_greeting(question):
        return "Hi! I'm ABL Chatbot, your Allied Bank assistant. I can help you with accounts, cards, digital banking, financing, and more. What would you like to know?"

    chunks = retrieve(question, top_k=top_k)

    if not chunks or chunks[0]["distance"] > DISTANCE_THRESHOLD:
        return (
            "That question doesn't fall under what I handle. "
            "I can help with Allied Bank's customer-facing products and services — "
            "accounts, cards, financing options, digital banking, and related processes. "
            "Please contact Allied Bank support for anything outside that scope."
        )

    prompt = build_prompt(question, chunks)
    messages = [{"role": "user", "content": prompt}]
    answer = ask_model(messages)

    return answer
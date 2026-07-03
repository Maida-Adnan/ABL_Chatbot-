# core/rag_pipeline.py
from core.retriever import retrieve
from core.prompt_builder import build_prompt
from core.ollama_client import ask_model
from core.memory import get_history, add_message

DISTANCE_THRESHOLD = 400

GREETINGS = {"hi", "hello", "hey", "salam", "assalam", "good morning", "good evening", "good afternoon", "how are you", "how r you"}


def is_greeting(question: str) -> bool:
    q = question.strip().lower()
    return any(g in q for g in GREETINGS)


def answer_question(question: str, session_id: str, top_k: int = 3) -> str:
    """
    Full RAG flow with conversation memory:
    1. Check for empty input or greeting
    2. Retrieve relevant chunks
    3. Check relevance threshold
    4. Build prompt with history + context + question
    5. Call model, save exchange to history, return answer
    """
    if not question or not question.strip():
        return "Please enter a question so I can help you."

    if is_greeting(question):
        greeting_response = "Hi! I'm ABL Chatbot, your Allied Bank assistant. I can help you with accounts, cards, digital banking, financing, and more. What would you like to know?"
        add_message(session_id, "user", question)
        add_message(session_id, "assistant", greeting_response)
        return greeting_response

    chunks = retrieve(question, top_k=top_k)

    if not chunks or chunks[0]["distance"] > DISTANCE_THRESHOLD:
        fallback = (
            "That question doesn't fall under what I handle. "
            "I can help with Allied Bank's customer-facing products and services — "
            "accounts, cards, financing options, digital banking, and related processes. "
            "Please contact Allied Bank support for anything outside that scope."
        )
        add_message(session_id, "user", question)
        add_message(session_id, "assistant", fallback)
        return fallback

    # Build messages: history + new RAG prompt
    history = get_history(session_id)
    prompt = build_prompt(question, chunks)

    messages = history + [{"role": "user", "content": prompt}]

    answer = ask_model(messages)

    # Save this exchange to history (save plain question, not the full RAG prompt)
    add_message(session_id, "user", question)
    add_message(session_id, "assistant", answer)

    return answer
from core.retriever import retrieve
from core.prompt_builder import build_prompt
from core.ollama_client import ask_model
from core.memory import get_history, add_message

DISTANCE_THRESHOLD = 400

GREETINGS = {"hi", "hello", "hey", "salam", "assalam", "good morning", "good evening", "good afternoon", "how are you", "how r you"}


def is_greeting(question: str) -> bool:
    q = question.strip().lower()
    return any(g in q for g in GREETINGS)


def rewrite_question(question: str, history: list[dict]) -> str:
    """
    Uses the model + conversation history to rewrite a question into a
    self-contained one, filling in the subject/product name from prior
    turns if the question doesn't already name it.
    Uses temperature=0 and a fixed seed so the same input always produces
    the same rewrite, keeping retrieval consistent across repeated queries.
    """
    if not history:
        return question

    history_text = "\n".join(
        f"{msg['role'].capitalize()}: {msg['content']}"
        for msg in history[-4:]  # last 2 exchanges is enough context
    )

    rewrite_prompt = f"""Given this conversation history:
{history_text}

Rewrite this question to be fully self-contained, explicitly naming the product/service being asked about based on the conversation history (replace pronouns like 'it', 'that', 'this' and fill in missing subjects).
Return ONLY the rewritten question, nothing else.

Question: {question}
Rewritten question:"""

    rewritten = ask_model(
        [{"role": "user", "content": rewrite_prompt}],
        temperature=0.0,
        seed=42
    )
    rewritten = rewritten.strip().strip('"').strip("'")

    if not rewritten or len(rewritten) > 200:
        return question

    return rewritten


def _passes_threshold(chunks) -> bool:
    return bool(chunks) and chunks[0]["distance"] <= DISTANCE_THRESHOLD


def _best_chunks(a, b):
    """Returns whichever chunk set has the lower (better) top-1 distance."""
    if not a:
        return b
    if not b:
        return a
    return b if b[0]["distance"] < a[0]["distance"] else a


def answer_question(question: str, session_id: str, top_k: int = 3) -> str:
    """
    Full RAG flow with conversation memory:
    1. Check for empty input or greeting
    2. Retrieve using the raw question
    3. If history exists, also rewrite the question using history and retrieve
       with that version — then keep whichever retrieval was more confident
       (lower distance), rather than guessing in advance which phrasing needs
       rewriting
    4. Check relevance threshold on the winning attempt
    5. Build prompt with history + context + question
    6. Call model, save exchange to history, return answer
    """
    if not question or not question.strip():
        return "Please enter a question so I can help you."

    if is_greeting(question):
        greeting_response = "Hi! I'm ABL Chatbot, your Allied Bank assistant. I can help you with accounts, cards, digital banking, financing, and more. What would you like to know?"
        add_message(session_id, "user", question)
        add_message(session_id, "assistant", greeting_response)
        return greeting_response

    history = get_history(session_id)

    chunks = retrieve(question, top_k=top_k)

    if history:
        rewritten_question = rewrite_question(question, history)
        if rewritten_question != question:
            rewritten_chunks = retrieve(rewritten_question, top_k=top_k)
            chunks = _best_chunks(chunks, rewritten_chunks)

    if not _passes_threshold(chunks):
        fallback = (
            "That question doesn't fall under what I handle. "
            "I can help with Allied Bank's customer-facing products and services — "
            "accounts, cards, financing options, digital banking, and related processes. "
            "Please contact Allied Bank support for anything outside that scope."
        )
        add_message(session_id, "user", question)
        add_message(session_id, "assistant", fallback)
        return fallback

    prompt = build_prompt(question, chunks)
    messages = history + [{"role": "user", "content": prompt}]

    answer = ask_model(messages, temperature=0.3)

    add_message(session_id, "user", question)
    add_message(session_id, "assistant", answer)

    return answer
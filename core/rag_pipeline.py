# core/rag_pipeline.py
from core.retriever import retrieve
from core.prompt_builder import build_prompt
from core.ollama_client import ask_model
from core.memory import get_history, add_message, clear_history

DISTANCE_THRESHOLD = 400
# Threshold to detect a confident, brand-new topic shift from a clear question
NEW_TOPIC_THRESHOLD = 150 

GREETINGS = {"hi", "hello", "hey", "salam", "assalam", "good morning", "good evening", "good afternoon", "how are you", "how r you"}


def is_greeting(question: str) -> bool:
    q = question.strip().lower()
    return any(g in q for g in GREETINGS)


def needs_context(question: str, history: list[dict]) -> bool:
    """
    Uses the local LLM to dynamically determine if the question relies 
    on conversational history to make sense, completely eliminating hardcoded lists.
    Outputs exactly one token ('YES' or 'NO') making execution fast.
    """
    if not history:
        return False # No history means it is inherently a fresh, standalone question

    classify_prompt = f"""You are a conversation analyzer. Determine if the following user question is fully self-contained, or if it requires previous context/history to understand what specific product or service it refers to.

User Question: "{question}"

Rules:
- If the question names a specific product or service explicitly, reply 'NO'.
- If the question is generic or uses vague pronouns (e.g., "What is the eligibility?", "What is its rate?", "Tell me more"), reply 'YES'.

Reply with exactly one word: 'YES' or 'NO'.
Classification:"""

    response = ask_model([{"role": "user", "content": classify_prompt}])
    return "YES" in response.upper()


def rewrite_question(question: str, history: list[dict]) -> str:
    """
    Uses the model + conversation history to rewrite a vague question
    into a self-contained one before database retrieval.
    """
    if not history:
        return question

    history_text = "\n".join(
        f"{msg['role'].capitalize()}: {msg['content']}"
        for msg in history[-4:]  # Last 2 complete exchanges provide ample context
    )

    rewrite_prompt = f"""You are an expert query refiner. Your single job is to replace vague pronouns like 'it', 'its', 'this', or 'that' with the exact, specific financial product name being discussed in the conversation history.

Conversation History:
{history_text}

Vague Question: "{question}"

Instructions:
1. Identify the primary product or service mentioned in the history (e.g., 'Allied Home Finance').
2. Rewrite the Vague Question to include that full name.
3. Return ONLY the final rewritten sentence. Do not include any introductory remarks, explanations, or quotes.

Rewritten question:"""

    rewritten = ask_model([{"role": "user", "content": rewrite_prompt}])
    rewritten = rewritten.strip().strip('"').strip("'")

    # Safety check: if rewriting failed or returned something weird, use original
    if not rewritten or len(rewritten) > 200:
        return question

    return rewritten


def answer_question(question: str, session_id: str, top_k: int = 3) -> str:
    """
    Full RAG flow with dynamic intent memory management:
    1. Check for empty input or basic greetings.
    2. Fetch chat history for the user session.
    3. Run fast grammar/intent classification to check if query lacks a subject.
    4. Rewrite query using history only if it needs context.
    5. If query was completely clear but hits a brand-new DB topic confidently, auto-clear history.
    6. Verify relevance threshold, construct prompt payload, execute final generation, and save turn.
    """
    if not question or not question.strip():
        return "Please enter a question so I can help you."

    if is_greeting(question):
        greeting_response = "Hi! I'm ABL Chatbot, your Allied Bank assistant. I can help you with accounts, cards, digital banking, financing, and more. What would you like to know?"
        add_message(session_id, "user", question)
        add_message(session_id, "assistant", greeting_response)
        return greeting_response

    # 1. Gather session history
    history = get_history(session_id) 

    # 2. Check if the question is complete or context-dependent
    vague_input = needs_context(question, history)

    # 3. Handle query transformation if context is missing
    retrieval_question = question
    if vague_input:
        retrieval_question = rewrite_question(question, history)

    # 4. Search ChromaDB vector space
    chunks = retrieve(retrieval_question, top_k=top_k)

    # 5. AUTOMATIC TOPIC SHIFT RESET
    # If the user asked an independent sentence (not vague), history exists, and the database 
    # yields an extremely strong match (low distance), we clear out the old topic history.
    if not vague_input and history and chunks:
        if chunks[0]["distance"] < NEW_TOPIC_THRESHOLD:
            clear_history(session_id)
            history = [] # Reset local pointer to an empty slate for this pipeline run

    # 6. Fallback checking against the distance limit
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

    # 7. Compile prompt context and invoke final generation model
    prompt = build_prompt(question, chunks)
    messages = history + [{"role": "user", "content": prompt}]

    answer = ask_model(messages)

    # 8. Save raw user input and final answer to session memory
    add_message(session_id, "user", question)
    add_message(session_id, "assistant", answer)

    return answer
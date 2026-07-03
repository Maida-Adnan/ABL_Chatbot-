# core/memory.py
from collections import defaultdict

# Stores conversation history per session
# { session_id: [ {"role": "user"/"assistant", "content": "..."}, ... ] }
_history: dict[str, list[dict]] = defaultdict(list)

MAX_MESSAGES = 6  # keep last 6 messages (3 exchanges)


def get_history(session_id: str) -> list[dict]:
    """Returns the conversation history for a session."""
    return _history[session_id]


def add_message(session_id: str, role: str, content: str) -> None:
    """Adds a message to the session history, keeping only the last MAX_MESSAGES."""
    _history[session_id].append({"role": role, "content": content})
    if len(_history[session_id]) > MAX_MESSAGES:
        _history[session_id] = _history[session_id][-MAX_MESSAGES:]


def clear_history(session_id: str) -> None:
    """Clears history for a session — useful for a 'new conversation' button."""
    _history[session_id] = []
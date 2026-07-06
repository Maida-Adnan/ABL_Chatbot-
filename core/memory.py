# core/memory.py
from collections import defaultdict

# Simulated in-memory database layout
# Format: { "session_id": [{"role": "user", "content": "..."}, ...] }
_history = defaultdict(list)

def get_history(session_id: str) -> list[dict]:
    """Retrieves the conversation history list for a specific session ID."""
    return _history[session_id]

def add_message(session_id: str, role: str, content: str):
    """Appends a new message turn to the specific session's history array."""
    _history[session_id].append({"role": role, "content": content})

def clear_history(session_id: str):
    """Wipes the conversation history array clean for a specific session ID."""
    if session_id in _history:
        _history[session_id] = []
import ollama
from core.config import OLLAMA_MODEL


def ask_model(messages: list[dict]) -> str:
    """
    Sends a list of chat messages to the configured Ollama model
    and returns just the text response.

    messages example:
    [{'role': 'user', 'content': 'Hello, who are you?'}]
    """
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages
        )
        return response['message']['content']
    except Exception as e:
        return f"ERROR: Could not get response from Ollama — {str(e)}"
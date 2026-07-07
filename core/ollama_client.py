import ollama
from core.config import OLLAMA_MODEL


def ask_model(messages: list[dict], temperature: float = 0.7, seed: int | None = None) -> str:
    """
    Sends a list of chat messages to the configured Ollama model
    and returns just the text response.

    temperature: lower = more deterministic/focused, higher = more varied.
    seed: fixes randomness for reproducible output when set.

    messages example:
    [{'role': 'user', 'content': 'Hello, who are you?'}]
    """
    try:
        options = {"temperature": temperature}
        if seed is not None:
            options["seed"] = seed

        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            options=options
        )
        return response['message']['content']
    except Exception as e:
        return f"ERROR: Could not get response from Ollama — {str(e)}"
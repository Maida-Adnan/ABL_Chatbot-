# core/embedder.py

#core/embedder.py — takes chunk text, calls Ollama's nomic-embed-text, returns a vector (list of floats).
import ollama

EMBED_MODEL = "nomic-embed-text"


def embed_text(text: str) -> list[float]:
    """Sends one chunk of text to Ollama and returns its embedding vector."""
    response = ollama.embeddings(model=EMBED_MODEL, prompt=text)
    return response["embedding"]


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Takes loader.py's chunk list and adds an 'embedding' key to each chunk."""
    embedded = []
    for chunk in chunks:
        vector = embed_text(chunk["text"])
        embedded.append({**chunk, "embedding": vector})
    return embedded
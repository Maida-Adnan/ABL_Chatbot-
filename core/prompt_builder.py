# core/prompt_builder.py

def build_prompt(question: str, chunks: list[dict]) -> str:
    """
    Combines retrieved chunks and the user's question into one prompt
    for the chat model. Instructs the model to only use the given
    context, and to say it doesn't know if the context doesn't help.
    """
    context_text = "\n\n---\n\n".join(chunk["text"] for chunk in chunks)

    prompt = f"""You are a helpful assistant for Allied Bank customers.
Answer the question using ONLY the context below.
If the context does not contain the answer, say clearly that you don't have that information — do not guess or use outside knowledge.

Context:
{context_text}

Question: {question}

Answer:"""

    return prompt
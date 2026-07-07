# core/prompt_builder.py

def build_prompt(question: str, chunks: list[dict]) -> str:
    """
    Combines retrieved chunks and the user's question into one prompt
    for the chat model. Instructs the model to only use the given
    context, and to say it doesn't know if the context doesn't help.
    """
    context_text = "\n\n---\n\n".join(chunk["text"] for chunk in chunks)

    prompt = f"""You are a helpful assistant for Allied Bank customers.
Answer the question using ONLY the context below. Be concise and clear.
Only answer about the specific product or service the question is asking about.
Do not mix information from multiple products.
Do not repeat yourself. Do not label your response with "Answer:".
If the context does not contain the answer, say clearly that you don't have that information.

Context:
{context_text}

Question: {question}"""

    return prompt
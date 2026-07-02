# core/retriever.py RETRIEVES  the chunk that relates the vector of the question to the vector of the text in chromadb which matches and has min distance 
from core.embedder import embed_text
from core.vectorstore import collection


def retrieve(question: str, top_k: int = 5) -> list[dict]:
    """
    Takes a user's question, embeds it, and searches ChromaDB for the
    top_k most similar chunks. Returns a list of dicts with text,
    metadata, and similarity distance (lower = more similar).
    """
    query_embedding = embed_text(question)    #goes into the embedder.py for this 

    results = collection.query(                #This specific line is the actual retrieval. This is where your code reaches inside your local database files (ChromaDB), scans all your stored text chunks, compares their vectors to your question's vector, and physically pulls out (retrieves) the top text matches and distance scores.

        query_embeddings=[query_embedding],
        n_results=top_k
    )

    matches = []
    for i in range(len(results["documents"][0])):
        matches.append({
            "text": results["documents"][0][i], 
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return matches
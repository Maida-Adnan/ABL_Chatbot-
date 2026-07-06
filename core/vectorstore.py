# core/vectorstore.py
import chromadb
from core.ollama_client import ask_model

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "abl_docs"

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)


def get_global_context(chunks: list[dict]) -> str:
    """
    Looks at the first few chunks of a document to dynamically extract 
    the overall product or topic context without any hardcoded names.
    """
    if not chunks:
        return "General Banking Information"
        
    # Combine text from the first 2 chunks to give the LLM ample header context
    sample_text = "\n".join([c["text"] for c in chunks[:2]])
    
    context_prompt = f"""Identify the specific financial product, loan scheme, card, or banking service this document is about based on its intro text.
Summarize it in one short, descriptive sentence (e.g., "This document details Allied Home Finance.").

Document text sample:
{sample_text[:1200]}

Summary sentence:"""

    response = ask_model([{"role": "user", "content": context_prompt}])
    return response.strip().replace("\n", " ")


def store_chunks(chunks: list[dict]) -> None:
    """
    Takes embedded chunks, injects an automated global context summary 
    into each text document dynamically to prevent cross-product vector bleeding,
    and saves them into the ChromaDB collection.
    """
    if not chunks:
        return

    # 1. Dynamically extract a single global product context sentence for this batch
    global_context = get_global_context(chunks)
    print(f"--- [INGESTION CONTEXT DETECTED]: {global_context} ---")

    # 2. Build the database arrays
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    embeddings = [c["embedding"] for c in chunks]
    metadatas = [
        {"source": c["source"], "title": c["title"] or ""}
        for c in chunks
    ]
    
    # 3. CONTEXT INJECTION LAYER
    # Prepend the dynamic global context line to the raw chunk text.
    # This mathematically bakes the true product subject right into ChromaDB's index space.
    enriched_documents = []
    for c in chunks:
        enriched_text = f"Product Context: {global_context}\nContent: {c['text']}"
        enriched_documents.append(enriched_text)

    # 4. Save to ChromaDB
    collection.add(
        ids=ids,
        documents=enriched_documents,  # Overwritten with our context-enriched text strings
        embeddings=embeddings,
        metadatas=metadatas,
    )
    print(f"Successfully stored {len(chunks)} context-protected chunks.")

def get_collection_count() -> int:
    """Returns the total number of chunks currently stored in the collection."""
    try:
        return collection.count()
    except Exception:
        return 0
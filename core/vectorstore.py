# core/vectorstore.py
import chromadb

CHROMA_PATH = "chroma_db"      # folder where Chroma saves its data on disk
COLLECTION_NAME = "abl_docs"   # name of your knowledge-base collection

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)


def store_chunks(chunks: list[dict]) -> None:
    """
    Takes embedded chunks (each with 'text', 'embedding', 'source', 'title')
    and saves them into the ChromaDB collection.
    """
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    documents = [c["text"] for c in chunks]
    embeddings = [c["embedding"] for c in chunks]
    metadatas = [
        {"source": c["source"], "title": c["title"] or ""}
        for c in chunks
    ]

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def get_collection_count() -> int:
    """Returns how many chunks are currently stored — useful for testing."""
    return collection.count()
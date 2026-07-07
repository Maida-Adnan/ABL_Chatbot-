import chromadb

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "abl_docs"

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)


def store_chunks(chunks: list[dict]) -> None:
    if not chunks:
        return

    existing_count = collection.count()
    ids = [f"chunk_{existing_count + i}" for i in range(len(chunks))]
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
    print(f"Successfully stored {len(chunks)} chunks.")


def get_collection_count() -> int:
    try:
        return collection.count()
    except Exception:
        return 0
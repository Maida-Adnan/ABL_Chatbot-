# run_ingest.py
from core.loader import load_documents
from core.embedder import embed_chunks
from core.vectorstore import store_chunks, get_collection_count

def main():
    print("Loading and chunking documents...")
    chunks = load_documents()
    print(f"Loaded {len(chunks)} chunks.")

    print("Embedding chunks (this may take a bit)...")
    embedded_chunks = embed_chunks(chunks)
    print("Embedding done.")

    print("Storing chunks in ChromaDB...")
    store_chunks(embedded_chunks)

    total = get_collection_count()
    print(f"Done. Total chunks now in ChromaDB: {total}")

if __name__ == "__main__":
    main()
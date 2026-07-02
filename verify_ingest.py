import chromadb

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("abl_docs")

print(f"Total chunks stored: {collection.count()}")

sample = collection.get(limit=1, include=["documents", "metadatas", "embeddings"])
print("\nSample chunk text (first 200 chars):")
print(sample["documents"][0][:200])
print("\nSample metadata:")
print(sample["metadatas"][0])
print("\nEmbedding vector length:", len(sample["embeddings"][0]))
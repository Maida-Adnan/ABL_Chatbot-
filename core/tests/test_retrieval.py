from core.retriever import retrieve

question = "What is the capital of France?"
results = retrieve(question, top_k=3)

for i, match in enumerate(results):
    print(f"\n--- Match {i+1} (distance: {match['distance']:.4f}) ---")
    print(f"Title: {match['metadata']['title']}")
    print(match['text'][:300])
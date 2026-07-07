from core.retriever import retrieve

results = retrieve("what is the eligibility for Allied Home Finance", top_k=3)
for i, r in enumerate(results):
    print(f"Match {i+1} - Distance: {r['distance']:.2f} - Title: {r['metadata']['title']}")
    print(r['text'][:200])
    print("---")
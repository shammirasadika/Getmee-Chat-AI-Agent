import chromadb

c = chromadb.HttpClient(host="localhost", port=8000)
col = c.get_collection("getmee_docs_dev")
results = col.get(include=["documents", "metadatas"])

print(f"Total docs: {len(results['ids'])}\n")
for i in range(len(results["ids"])):
    doc = results["documents"][i]
    print(f"--- Chunk {i+1} ---")
    print(doc[:300])
    print()

from chroma_client import get_collection

collection = get_collection()

# Print current results in the collection
results = collection.get()
print(results)

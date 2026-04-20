import chromadb

client = chromadb.HttpClient(host="localhost", port=8000)

# List all collections
def list_collections_and_counts():
    collections = client.list_collections()
    if not collections:
        print("No collections found.")
        return
    for col in collections:
        name = col.name if hasattr(col, 'name') else col['name']
        print(f"Collection: {name}")
        collection = client.get_collection(name)
        docs = collection.get()
        count = len(docs['ids']) if 'ids' in docs else 0
        print(f"  Document count: {count}")
        print()

if __name__ == "__main__":
    list_collections_and_counts()

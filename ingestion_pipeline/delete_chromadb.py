from chroma_client import get_collection

collection = get_collection()

# Delete all records in the collection
ids = collection.get()["ids"]
if ids:
    collection.delete(ids=ids)
    print(f"Deleted {len(ids)} records from the collection.")
else:
    print("No records to delete.")

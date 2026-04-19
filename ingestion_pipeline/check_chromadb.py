from chroma_client import get_chroma_client

client = get_chroma_client()

print("Testing Chroma connection...")
print(client.heartbeat())
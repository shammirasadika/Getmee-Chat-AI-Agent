from app.clients.chroma_client import ChromaClient

class RetrievalService:
    def __init__(self):
        self.chroma = ChromaClient()

    async def retrieve(self, query: str, top_k: int = 5):
        return self.chroma.query(query, top_k=top_k)

from app.clients.chroma_client import ChromaClient

# Distance threshold — lower distance = better match in ChromaDB
# Relaxed to 2.0 to allow partial matches and avoid over-filtering
DISTANCE_THRESHOLD = 2.0

class RetrievalService:
    def __init__(self):
        self.chroma = ChromaClient()

    async def retrieve(self, query: str, top_k: int = 5):
        return self.chroma.query(query, top_k=top_k)

    @staticmethod
    def has_relevant_results(retrieved: dict, threshold: float = DISTANCE_THRESHOLD) -> bool:
        """Check if retrieval results contain relevant documents based on distance scores."""
        if not retrieved:
            print("[Retrieval] No retrieved data (None)", flush=True)
            return False
        documents = retrieved.get('documents', [])
        distances = retrieved.get('distances', [])
        # No documents at all
        if not documents or not any(documents):
            print("[Retrieval] No documents found", flush=True)
            return False
        # Flatten documents to check they have actual content
        flat_docs = [doc for group in documents for doc in group if doc and doc.strip()]
        if not flat_docs:
            print("[Retrieval] Documents are empty after filtering", flush=True)
            return False
        # Check distances if available
        if distances:
            flat_distances = [d for group in distances for d in group]
            if flat_distances:
                best = min(flat_distances)
                print(f"[Retrieval] Best distance: {best:.3f} (threshold: {threshold}) | Docs: {len(flat_docs)}", flush=True)
                return best < threshold
        # If no distances returned, documents exist so assume relevant
        print(f"[Retrieval] No distances available, {len(flat_docs)} docs found — assuming relevant", flush=True)
        return True

    @staticmethod
    def get_best_distance(retrieved: dict) -> float:
        """Return the best (lowest) distance score from results."""
        distances = retrieved.get('distances', [])
        if distances:
            flat = [d for group in distances for d in group]
            if flat:
                return min(flat)
        return float('inf')

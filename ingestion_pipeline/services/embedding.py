from sentence_transformers import SentenceTransformer

# Load the model once at module level for efficiency
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384-dim

def generate_embedding(text):
    """
    Generate a 384-dim embedding for the given text using sentence-transformers.
    """
    embedding = model.encode(text)
    return embedding.tolist()

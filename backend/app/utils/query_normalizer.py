import re
import unicodedata


_CONTRACTIONS = {
    "can't": "cannot",
    "won't": "will not",
    "n't": " not",
    "it's": "it is",
    "i'm": "i am",
    "you're": "you are",
    "we're": "we are",
    "they're": "they are",
    "that's": "that is",
    "there's": "there is",
    "what's": "what is",
}


def _normalize_token(token: str) -> str:
    token = token.strip("'_")
    if token.endswith("'s"):
        token = token[:-2]

    # Lightweight stemming/canonicalization to reduce form mismatch.
    if len(token) > 4 and token.endswith("ies"):
        token = token[:-3] + "y"
    elif len(token) > 4 and token.endswith("es") and token[-3] in {"s", "x", "z", "h"}:
        token = token[:-2]
    elif len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        token = token[:-1]

    if len(token) > 5 and token.endswith("ing"):
        token = token[:-3]
    elif len(token) > 4 and token.endswith("ed"):
        token = token[:-2]

    return token


def normalize_query_text(text: str) -> str:
    """Return a retrieval-friendly normalized query string."""
    if not text:
        return ""

    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("’", "'").lower().strip()

    for src, dst in _CONTRACTIONS.items():
        normalized = normalized.replace(src, dst)

    normalized = re.sub(r"[^a-z0-9áéíóúñü\s']", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if not normalized:
        return ""

    tokens = [_normalize_token(tok) for tok in normalized.split()]
    tokens = [tok for tok in tokens if tok]
    return " ".join(tokens)


def build_retrieval_query(original_query: str) -> str:
    """Combine original + normalized forms to improve vector recall."""
    normalized = normalize_query_text(original_query)
    if not normalized:
        return original_query

    original_clean = (original_query or "").strip()
    if not original_clean:
        return normalized

    if original_clean.lower() == normalized:
        return original_clean

    # Keep both forms so embeddings see natural phrasing plus canonical terms.
    return f"{original_clean}\n{normalized}"

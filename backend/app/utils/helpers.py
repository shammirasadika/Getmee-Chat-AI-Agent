# Common stopwords for name detection and other NLP tasks
NAME_DETECTION_STOPWORDS = set([
    'able', 'about', 'account', 'again', 'am', 'an', 'and', 'are', 'as', 'at', 'be', 'because', 'been', 'but', 'by', 'can', 'cannot', 'could', 'did', 'do', 'does', 'doing', 'for', 'from', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'me', 'more', 'most', 'my', 'myself', 'no', 'not', 'of', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she', 'should', 'so', 'some', 'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'would', 'you', 'your', 'yours', 'yourself', 'yourselves', 'able', 'login', 'log', 'in', 'out', 'ready', 'happy', 'sad', 'good', 'bad', 'ok', 'okay', 'fine', 'thanks', 'thank', 'problem', 'issue', 'help', 'support', 'team', 'account', 'reset', 'password', 'email', 'contact', 'question', 'answer', 'user', 'admin', 'manager', 'customer', 'service', 'bot', 'assistant', 'ai', 'robot', 'system', 'test', 'testing', 'demo', 'sample', 'example', 'feedback', 'satisfied', 'unsatisfied', 'cannot', 'unable', 'not', 'to', 'my', 'name', 'is', 'i', 'am', "i'm", 'me', 'myself', 'your', 'you', 'he', 'she', 'it', 'we', 'they', 'this', 'that', 'these', 'those', 'here', 'there', 'where', 'when', 'why', 'how', 'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'from', 'up', 'down', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'
])
import re
from app.utils.query_normalizer import normalize_query_text

def safe_get(d: dict, key: str, default=None):
    return d[key] if key in d else default


# Minimum length for a chunk to be considered meaningful
MIN_MEANINGFUL_LENGTH = 30
# Max ratio of non-alpha characters allowed
MAX_NOISE_RATIO = 0.6
# Minimum keyword overlap ratio to consider a chunk relevant to the query
MIN_RELEVANCE_OVERLAP = 0.25
# Minimum confidence (overlap ratio) to trust primary retrieval without fallback
MIN_PRIMARY_CONFIDENCE = 0.5
# Relaxed overlap for cross-language fallback (translated query vs same-language chunks)
# Lower than primary because translation may not perfectly match KB vocabulary
MIN_CROSS_LANG_OVERLAP = 0.15

# Common stopwords to ignore during relevance matching (en + es)
_STOPWORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'can', 'shall', 'to', 'of', 'in', 'for',
    'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'between', 'out', 'off', 'over',
    'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
    'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
    'same', 'so', 'than', 'too', 'very', 'just', 'because', 'but', 'and',
    'or', 'if', 'while', 'about', 'up', 'what', 'which', 'who', 'whom',
    'this', 'that', 'these', 'those', 'i', 'me', 'my', 'myself', 'we',
    'our', 'you', 'your', 'he', 'him', 'his', 'she', 'her', 'it', 'its',
    'they', 'them', 'their',
    # Generic high-frequency verbs — too ambiguous to be meaningful topic signals
    # e.g. "not working" → "work" would falsely match "onboarding work"
    'work', 'use', 'make', 'get', 'set', 'run', 'see', 'find', 'take',
    'come', 'put', 'say', 'try', 'ask', 'call', 'show', 'help', 'let',
    'need', 'want', 'give', 'keep', 'send', 'open', 'close', 'log',
    'go', 'look', 'turn', 'start', 'stop', 'give', 'seem', 'feel',
    # Spanish stopwords
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del',
    'en', 'y', 'o', 'que', 'es', 'por', 'con', 'para', 'como', 'pero',
    'su', 'al', 'lo', 'se', 'le', 'les', 'me', 'mi', 'nos', 'no', 'si',
    'yo', 'tu', 'te', 'ya', 'más', 'muy', 'este', 'esta', 'esto', 'ese',
    'esa', 'eso', 'hay', 'ser', 'tener', 'hacer', 'poder', 'hola',
}


def _extract_keywords(text: str) -> set:
    """Extract meaningful keywords from text, lowercased, stopwords removed."""
    normalized = normalize_query_text(text)
    words = re.findall(r'[a-záéíóúñü]{3,}', normalized)
    return {w for w in words if w not in _STOPWORDS}


def clean_context_chunk(text: str) -> str:
    """Remove noisy data from retrieved context chunks."""
    # Remove email headers (From:, To:, Subject:, Date:, etc.)
    text = re.sub(r'(?i)^(from|to|cc|bcc|subject|date|sent|received)\s*:.*$', '', text, flags=re.MULTILINE)
    # Remove email addresses
    text = re.sub(r'[\w.\-+]+@[\w.\-]+\.\w+', '', text)
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove CSV-like patterns (lines with many commas or pipes)
    text = re.sub(r'^[^,\n]*(?:,[^,\n]*){4,}$', '', text, flags=re.MULTILINE)
    # Remove lines that are mostly numbers, dates, and delimiters
    text = re.sub(r"^[\d\s,\-/:']+$", '', text, flags=re.MULTILINE)
    # Remove pipe-delimited table rows
    text = re.sub(r'^.*\|.*\|.*\|.*$', '', text, flags=re.MULTILINE)
    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def is_meaningful_chunk(text: str) -> bool:
    """Check if a cleaned chunk contains meaningful, usable content."""
    if not text or len(text.strip()) < MIN_MEANINGFUL_LENGTH:
        return False
    stripped = text.strip()
    # Reject if mostly non-alphabetic characters (numbers, punctuation, delimiters)
    alpha_chars = sum(1 for c in stripped if c.isalpha())
    if alpha_chars == 0:
        return False
    noise_ratio = 1 - (alpha_chars / len(stripped))
    if noise_ratio > MAX_NOISE_RATIO:
        return False
    # Reject if it looks like CSV (many commas relative to length)
    comma_count = stripped.count(',')
    if comma_count > len(stripped) / 15:
        return False
    # Reject if too many broken fragments (lots of single-word lines)
    lines = [l.strip() for l in stripped.split('\n') if l.strip()]
    if lines:
        short_lines = sum(1 for l in lines if len(l.split()) <= 2)
        if len(lines) > 2 and short_lines / len(lines) > 0.7:
            return False
    # Reject if text is a raw ticket/ID dump (mostly IDs and statuses)
    if re.search(r'(?:Solved|Open|Pending|Closed)[,\s]', stripped) and comma_count > 3:
        return False
    return True


def is_relevant_to_query(chunk: str, query: str) -> tuple:
    """Check if a chunk is semantically relevant to the user query using keyword overlap.
    Returns (is_relevant: bool, reason: str, overlap_ratio: float).
    """
    query_keywords = _extract_keywords(query)
    if not query_keywords:
        return True, "no query keywords to evaluate", 1.0
    chunk_keywords = _extract_keywords(chunk)
    if not chunk_keywords:
        return False, "chunk has no extractable keywords", 0.0
    # Check how many query keywords appear in the chunk
    overlap = query_keywords & chunk_keywords
    overlap_ratio = len(overlap) / len(query_keywords)
    if overlap_ratio >= MIN_RELEVANCE_OVERLAP:
        return True, f"overlap={overlap}", overlap_ratio
    return False, f"low overlap {overlap_ratio:.2f} (need {MIN_RELEVANCE_OVERLAP}), query_kw={query_keywords}, chunk_kw={list(chunk_keywords)[:8]}", overlap_ratio


def filter_relevant_chunks(chunks: list, query: str, is_cross_language: bool = False) -> tuple:
    """Filter chunks to only those relevant to the query.
    For cross-language fallback, apply keyword matching with a relaxed threshold
    (the query is already translated to the chunk language).
    Returns (relevant, rejected_count, rejection_reasons, max_overlap).
    max_overlap is the highest overlap ratio among accepted chunks (0.0-1.0).
    """
    relevant = []
    rejected = 0
    reasons = []
    max_overlap = 0.0
    threshold = MIN_CROSS_LANG_OVERLAP if is_cross_language else MIN_RELEVANCE_OVERLAP
    for i, chunk in enumerate(chunks):
        query_keywords = _extract_keywords(query)
        chunk_keywords = _extract_keywords(chunk)
        # Compute keyword overlap
        if not query_keywords:
            # Cannot evaluate — accept on distance only
            relevant.append(chunk)
            max_overlap = max(max_overlap, 0.5)
            reasons.append(f"chunk {i+1}: accepted (no query keywords, distance only) [cross_lang={is_cross_language}]")
            continue
        if not chunk_keywords:
            rejected += 1
            reasons.append(f"chunk {i+1}: REJECTED (no chunk keywords) [cross_lang={is_cross_language}]")
            continue
        overlap = query_keywords & chunk_keywords
        ratio = len(overlap) / len(query_keywords)
        if ratio >= threshold:
            relevant.append(chunk)
            max_overlap = max(max_overlap, ratio)
            signal = "keyword match" if ratio >= MIN_RELEVANCE_OVERLAP else "relaxed keyword match"
            reasons.append(
                f"chunk {i+1}: accepted ({signal}, overlap={overlap}, ratio={ratio:.2f}, "
                f"threshold={threshold}) [cross_lang={is_cross_language}]"
            )
        else:
            rejected += 1
            reasons.append(
                f"chunk {i+1}: REJECTED (low overlap ratio={ratio:.2f}, need {threshold}, "
                f"query_kw={query_keywords}, chunk_kw={list(chunk_keywords)[:8]}) [cross_lang={is_cross_language}]"
            )
    return relevant, rejected, reasons, max_overlap


def is_language_clean(text: str, language: str) -> bool:
    """Check if the response text is predominantly in the expected language."""
    if not text or len(text) < 10:
        return True
    try:
        from langdetect import detect
        detected = detect(text)
        detected = detected.split('-')[0]
        return detected == language
    except Exception:
        return True  # If detection fails, assume clean

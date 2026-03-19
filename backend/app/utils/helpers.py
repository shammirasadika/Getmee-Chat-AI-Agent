def safe_get(d: dict, key: str, default=None):
    return d[key] if key in d else default

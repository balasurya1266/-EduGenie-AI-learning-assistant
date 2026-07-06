"""Text preprocessing and cleaning utilities."""
import re
import html


def clean_text(text: str) -> str:
    text = html.unescape(text.strip())
    text = re.sub(r"\s+", " ", text)
    return text


def truncate(text: str, max_len: int = 500) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i : i + chunk_size]
        chunks.append(" ".join(chunk_words))
        i += chunk_size - overlap
    return chunks if chunks else [text]


def extract_keywords(text: str, limit: int = 10) -> list[str]:
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    freq: dict[str, int] = {}
    stop = {"that", "this", "with", "from", "have", "been", "were", "they", "their", "about"}
    for w in words:
        if w not in stop:
            freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:limit]]

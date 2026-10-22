"""Small local knowledge base and transparent lexical retrieval."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "knowledge_base.json"


def load_documents() -> list[dict[str, str]]:
    with DATA_PATH.open(encoding="utf-8") as handle:
        data: Any = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("Knowledge base must be a JSON list")
    return data


STOP_WORDS = {"a", "an", "and", "are", "for", "how", "i", "is", "it", "of", "on", "the", "to", "what", "with", "does", "should", "my", "can", "get"}

def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in STOP_WORDS}


def search_knowledge_base(query: str, limit: int = 3) -> list[dict[str, str | float]]:
    """Rank documents by a simple, explainable token-overlap score.

    This intentionally small baseline avoids pretending to be a vector database.
    Swap this function for hybrid BM25 + embeddings retrieval when needed.
    """
    query_tokens = _tokens(query)
    if not query_tokens:
        return []

    ranked: list[tuple[float, dict[str, str]]] = []
    for doc in load_documents():
        text = f"{doc.get('title', '')} {doc.get('content', '')}"
        doc_tokens = _tokens(text)
        overlap = len(query_tokens & doc_tokens)
        score = overlap / max(1, len(query_tokens))
        if score > 0:
            ranked.append((score, doc))

    ranked.sort(key=lambda item: (-item[0], item[1].get("id", "")))
    return [
        {"id": doc["id"], "title": doc["title"], "content": doc["content"], "score": round(score, 3)}
        for score, doc in ranked[: max(1, limit)]
    ]

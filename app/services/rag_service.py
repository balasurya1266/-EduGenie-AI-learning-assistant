"""RAG service with vector embeddings using Gemini."""
import math
from typing import Optional

from app.ai.gemini_client import GeminiClient, gemini_client
from app.config import CHUNK_OVERLAP, CHUNK_SIZE
from app.models import database as db
from app.utils.text_processing import chunk_text, clean_text


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class RAGService:
    async def index_document(
        self,
        user_id: str,
        filename: str,
        text: str,
        api_key: Optional[str] = None,
    ) -> dict:
        client = GeminiClient(api_key) if api_key else gemini_client
        text = clean_text(text)
        chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)

        embeddings = []
        for chunk in chunks:
            emb = await client.embed(chunk)
            embeddings.append({"text": chunk, "embedding": emb})

        doc_id = db.new_id()
        record = {
            "DocumentID": doc_id,
            "UserID": user_id,
            "Filename": filename,
            "TextLength": len(text),
            "Chunks": embeddings,
            "CreatedAt": db.now_iso(),
        }
        db.insert("documents", record)
        return record

    async def get_relevant_context(
        self,
        user_id: str,
        document_id: str,
        query: str,
        api_key: Optional[str] = None,
        top_k: int = 3,
    ) -> str:
        doc = db.find_one("documents", DocumentID=document_id, UserID=user_id)
        if not doc or not doc.get("Chunks"):
            return ""

        client = GeminiClient(api_key) if api_key else gemini_client
        query_emb = await client.embed(query)

        scored = []
        for chunk in doc["Chunks"]:
            score = _cosine_similarity(query_emb, chunk["embedding"])
            scored.append((score, chunk["text"]))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [text for _, text in scored[:top_k]]
        return "\n\n".join(top_chunks)

    def list_documents(self, user_id: str) -> list[dict]:
        docs = db.find_all("documents", UserID=user_id)
        return [
            {
                "id": d["DocumentID"],
                "filename": d["Filename"],
                "text_length": d.get("TextLength", 0),
                "created_at": d.get("CreatedAt"),
            }
            for d in docs
        ]


rag_service = RAGService()

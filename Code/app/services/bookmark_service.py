"""Bookmark service for saving AI responses."""
from app.models import database as db


class BookmarkService:
    def add(self, user_id: str, query_id: str, title: str = None) -> dict:
        existing = db.find_one("bookmarks", UserID=user_id, QueryID=query_id)
        if existing:
            return existing
        record = {
            "BookmarkID": db.new_id(),
            "UserID": user_id,
            "QueryID": query_id,
            "Title": title or "Bookmarked Response",
            "CreatedAt": db.now_iso(),
        }
        db.insert("bookmarks", record)
        return record

    def remove(self, user_id: str, bookmark_id: str) -> bool:
        bm = db.find_one("bookmarks", BookmarkID=bookmark_id, UserID=user_id)
        if not bm:
            return False
        return db.delete("bookmarks", bookmark_id, "BookmarkID")

    def list(self, user_id: str) -> list[dict]:
        bookmarks = db.find_all("bookmarks", UserID=user_id)
        bookmarks.sort(key=lambda x: x.get("CreatedAt", ""), reverse=True)
        result = []
        for bm in bookmarks:
            query = db.find_one("user_queries", QueryID=bm["QueryID"])
            response = db.find_one("ai_responses", QueryID=bm["QueryID"])
            result.append({
                "id": bm["BookmarkID"],
                "title": bm["Title"],
                "query": query["QueryText"] if query else "",
                "response": response["ResponseText"][:200] if response else "",
                "type": query["QueryType"] if query else "",
                "created_at": bm["CreatedAt"],
            })
        return result


bookmark_service = BookmarkService()

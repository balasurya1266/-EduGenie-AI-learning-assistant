"""History and query persistence service."""
from typing import Optional

from app.models import database as db


class HistoryService:
    def create_query(self, user_id: str, query_type: str, query_text: str) -> dict:
        record = {
            "QueryID": db.new_id(),
            "UserID": user_id,
            "QueryType": query_type,
            "QueryText": query_text,
            "CreatedAt": db.now_iso(),
        }
        db.insert("user_queries", record)
        return record

    def save_response(self, query_id: str, response_text: str, model_used: str) -> dict:
        record = {
            "ResponseID": db.new_id(),
            "QueryID": query_id,
            "ResponseText": response_text,
            "ModelUsed": model_used,
            "CreatedAt": db.now_iso(),
        }
        db.insert("ai_responses", record)
        return record

    def save_quiz_questions(self, query_id: str, questions: list[dict]) -> list[dict]:
        saved = []
        for q in questions:
            record = {
                "QuizID": db.new_id(),
                "QueryID": query_id,
                "QuestionText": q.get("question", ""),
                "OptionA": q.get("option_a", ""),
                "OptionB": q.get("option_b", ""),
                "OptionC": q.get("option_c", ""),
                "OptionD": q.get("option_d", ""),
                "CorrectOption": q.get("correct_option", "A"),
                "Explanation": q.get("explanation", ""),
                "CreatedAt": db.now_iso(),
            }
            db.insert("quizzes", record)
            saved.append(record)
        return saved

    def save_summary(
        self, query_id: str, original_text: str, summary_text: str, model_used: str
    ) -> dict:
        record = {
            "SummaryID": db.new_id(),
            "QueryID": query_id,
            "OriginalText": original_text[:5000],
            "SummaryText": summary_text,
            "ModelUsed": model_used,
            "CreatedAt": db.now_iso(),
        }
        db.insert("summaries", record)
        return record

    def save_learning_path(
        self, query_id: str, topic: str, level: str, content: str
    ) -> dict:
        record = {
            "PathID": db.new_id(),
            "QueryID": query_id,
            "Topic": topic,
            "Level": level,
            "RecommendedTopics": content,
            "CreatedAt": db.now_iso(),
        }
        db.insert("learning_paths", record)
        return record

    def get_user_history(self, user_id: str, limit: int = 50) -> list[dict]:
        queries = db.find_all("user_queries", UserID=user_id)
        queries.sort(key=lambda x: x.get("CreatedAt", ""), reverse=True)
        results = []
        for q in queries[:limit]:
            response = db.find_one("ai_responses", QueryID=q["QueryID"])
            results.append({
                "query_id": q["QueryID"],
                "type": q["QueryType"],
                "text": q["QueryText"],
                "created_at": q["CreatedAt"],
                "response": response["ResponseText"] if response else None,
                "model": response["ModelUsed"] if response else None,
            })
        return results

    def search_history(self, user_id: str, term: str) -> list[dict]:
        history = self.get_user_history(user_id, limit=200)
        term_lower = term.lower()
        return [
            h for h in history
            if term_lower in h["text"].lower()
            or (h.get("response") and term_lower in h["response"].lower())
        ]

    def delete_user_history(self, user_id: str) -> int:
        queries = db.find_all("user_queries", UserID=user_id)
        count = 0
        for q in queries:
            db.delete_where("ai_responses", QueryID=q["QueryID"])
            db.delete_where("quizzes", QueryID=q["QueryID"])
            db.delete_where("summaries", QueryID=q["QueryID"])
            db.delete_where("learning_paths", QueryID=q["QueryID"])
            db.delete("user_queries", q["QueryID"], "QueryID")
            count += 1
        return count

    def get_response_by_query(self, query_id: str) -> Optional[dict]:
        return db.find_one("ai_responses", QueryID=query_id)


history_service = HistoryService()

"""Learning analytics and streak tracking."""
from datetime import date

from app.models import database as db


class AnalyticsService:
    def get_stats(self, user_id: str) -> dict:
        stats = db.find_one("analytics", UserID=user_id)
        if not stats:
            return self._default_stats()
        return stats

    def _default_stats(self) -> dict:
        return {
            "QuestionsAsked": 0,
            "QuizzesTaken": 0,
            "SummariesCreated": 0,
            "LearningPaths": 0,
            "Streak": 0,
            "Badges": [],
            "WeeklyGoal": 10,
            "WeeklyProgress": 0,
        }

    def increment(self, user_id: str, field: str) -> None:
        stats = db.find_one("analytics", UserID=user_id)
        if not stats:
            return
        today = date.today().isoformat()
        last_active = stats.get("LastActiveDate", "")
        streak = stats.get("Streak", 0)

        if last_active == today:
            pass
        elif last_active and self._is_yesterday(last_active, today):
            streak += 1
        else:
            streak = 1

        updates = {
            field: stats.get(field, 0) + 1,
            "Streak": streak,
            "LastActiveDate": today,
            "WeeklyProgress": stats.get("WeeklyProgress", 0) + 1,
        }
        db.update("analytics", user_id, "UserID", updates)
        self._check_badges(user_id, updates)

    def _is_yesterday(self, last: str, today: str) -> bool:
        from datetime import datetime, timedelta
        try:
            last_date = datetime.fromisoformat(last).date()
            today_date = datetime.fromisoformat(today).date()
            return (today_date - last_date).days == 1
        except ValueError:
            return False

    def _check_badges(self, user_id: str, stats: dict) -> None:
        badges = set(stats.get("Badges", []))
        if stats.get("QuestionsAsked", 0) >= 10:
            badges.add("Curious Mind")
        if stats.get("QuizzesTaken", 0) >= 5:
            badges.add("Quiz Master")
        if stats.get("Streak", 0) >= 7:
            badges.add("Week Warrior")
        if stats.get("SummariesCreated", 0) >= 5:
            badges.add("Note Ninja")
        db.update("analytics", user_id, "UserID", {"Badges": list(badges)})

    def get_dashboard_data(self, user_id: str) -> dict:
        stats = self.get_stats(user_id)
        recent = db.find_all("user_queries", UserID=user_id)
        recent.sort(key=lambda x: x.get("CreatedAt", ""), reverse=True)
        return {
            "questions_asked": stats.get("QuestionsAsked", 0),
            "quizzes": stats.get("QuizzesTaken", 0),
            "summaries": stats.get("SummariesCreated", 0),
            "learning_paths": stats.get("LearningPaths", 0),
            "streak": stats.get("Streak", 0),
            "badges": stats.get("Badges", []),
            "weekly_goal": stats.get("WeeklyGoal", 10),
            "weekly_progress": stats.get("WeeklyProgress", 0),
            "recent_activities": [
                {"type": r["QueryType"], "text": r["QueryText"][:80], "date": r["CreatedAt"]}
                for r in recent[:5]
            ],
        }


analytics_service = AnalyticsService()

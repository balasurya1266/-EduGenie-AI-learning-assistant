"""Authentication and user management service."""
from typing import Optional

from app.models import database as db
from app.utils.security import create_access_token, hash_password, verify_password


class AuthService:
    def signup(self, username: str, email: str, password: str) -> dict:
        if db.find_one("users", Email=email.lower()):
            raise ValueError("Email already registered")
        if db.find_one("users", UserName=username):
            raise ValueError("Username already taken")

        user = {
            "UserID": db.new_id(),
            "UserName": username,
            "Email": email.lower(),
            "PasswordHash": hash_password(password),
            "CreatedAt": db.now_iso(),
        }
        db.insert("users", user)
        self._init_user_data(user["UserID"])
        return user

    def login(self, email: str, password: str, remember: bool = False) -> tuple[dict, str]:
        user = db.find_one("users", Email=email.lower())
        if not user or not verify_password(password, user["PasswordHash"]):
            raise ValueError("Invalid email or password")
        token = create_access_token(user["UserID"], remember)
        return user, token

    def get_user(self, user_id: str) -> Optional[dict]:
        return db.find_one("users", UserID=user_id)

    def update_profile(self, user_id: str, username: str = None, email: str = None) -> dict:
        updates = {}
        if username:
            existing = db.find_one("users", UserName=username)
            if existing and existing["UserID"] != user_id:
                raise ValueError("Username already taken")
            updates["UserName"] = username
        if email:
            existing = db.find_one("users", Email=email.lower())
            if existing and existing["UserID"] != user_id:
                raise ValueError("Email already in use")
            updates["Email"] = email.lower()
        if not updates:
            return self.get_user(user_id)
        return db.update("users", user_id, "UserID", updates)

    def _init_user_data(self, user_id: str) -> None:
        db.insert("user_settings", {
            "UserID": user_id,
            "DarkMode": False,
            "Language": "en",
            "GeminiAPIKey": "",
            "CreatedAt": db.now_iso(),
        })
        db.insert("analytics", {
            "UserID": user_id,
            "QuestionsAsked": 0,
            "QuizzesTaken": 0,
            "SummariesCreated": 0,
            "LearningPaths": 0,
            "Streak": 0,
            "LastActiveDate": db.now_iso()[:10],
            "Badges": ["Welcome"],
            "WeeklyGoal": 10,
            "WeeklyProgress": 0,
        })


auth_service = AuthService()

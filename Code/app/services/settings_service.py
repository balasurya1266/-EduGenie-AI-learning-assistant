"""User settings service."""
from typing import Optional

from app.models import database as db


class SettingsService:
    def get(self, user_id: str) -> dict:
        settings = db.find_one("user_settings", UserID=user_id)
        if not settings:
            return {"DarkMode": False, "Language": "en", "GeminiAPIKey": ""}
        return settings

    def update(self, user_id: str, **kwargs) -> dict:
        allowed = {"DarkMode", "Language", "GeminiAPIKey"}
        updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if not updates:
            return self.get(user_id)
        existing = db.find_one("user_settings", UserID=user_id)
        if existing:
            return db.update("user_settings", user_id, "UserID", updates)
        updates["UserID"] = user_id
        updates["CreatedAt"] = db.now_iso()
        db.insert("user_settings", updates)
        return updates

    def get_api_key(self, user_id: str) -> Optional[str]:
        settings = self.get(user_id)
        key = settings.get("GeminiAPIKey", "")
        return key if key else None


settings_service = SettingsService()

"""FastAPI dependencies for authentication."""
from typing import Optional

from fastapi import Cookie, HTTPException, Request

from app.services.auth_service import auth_service
from app.utils.security import decode_token


async def get_current_user_id(
    request: Request,
    access_token: Optional[str] = Cookie(None),
) -> Optional[str]:
    token = access_token or request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return None
    return decode_token(token)


async def require_user(
    request: Request,
    access_token: Optional[str] = Cookie(None),
) -> dict:
    user_id = await get_current_user_id(request, access_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = auth_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

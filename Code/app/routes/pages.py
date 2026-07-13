"""Page routes serving Jinja2 templates."""
from fastapi import APIRouter, Cookie, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import APP_NAME, TEMPLATES_DIR
from app.dependencies import get_current_user_id, require_user
from app.services.analytics_service import analytics_service
from app.services.auth_service import auth_service
from app.services.bookmark_service import bookmark_service
from app.services.history_service import history_service
from app.services.settings_service import settings_service

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _ctx(user: dict = None, **extra):
    base = {
        "app_name": APP_NAME,
        "user": user,
    }
    base.update(extra)
    return base


@router.get("/", response_class=HTMLResponse)
async def landing(request: Request, access_token: str = Cookie(None)):
    user_id = await get_current_user_id(request, access_token)
    user = auth_service.get_user(user_id) if user_id else None
    return templates.TemplateResponse(request, "landing.html", _ctx(user))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", _ctx())


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(request, "signup.html", _ctx())


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: dict = Depends(require_user)):
    data = analytics_service.get_dashboard_data(user["UserID"])
    settings = settings_service.get(user["UserID"])
    return templates.TemplateResponse(
        request,
        "dashboard/home.html",
        _ctx(user, stats=data, settings=settings, active="home"),
    )


@router.get("/ask", response_class=HTMLResponse)
async def ask_page(request: Request, user: dict = Depends(require_user)):
    return templates.TemplateResponse(
        request,
        "dashboard/ask.html",
        _ctx(user, active="ask"),
    )


@router.get("/explain", response_class=HTMLResponse)
async def explain_page(request: Request, user: dict = Depends(require_user)):
    return templates.TemplateResponse(
        request, "dashboard/explain.html", _ctx(user, active="explain")
    )


@router.get("/quiz", response_class=HTMLResponse)
async def quiz_page(request: Request, user: dict = Depends(require_user)):
    return templates.TemplateResponse(
        request, "dashboard/quiz.html", _ctx(user, active="quiz")
    )


@router.get("/summary", response_class=HTMLResponse)
async def summary_page(request: Request, user: dict = Depends(require_user)):
    return templates.TemplateResponse(
        request, "dashboard/summary.html", _ctx(user, active="summary")
    )


@router.get("/learning-path", response_class=HTMLResponse)
async def learning_path_page(request: Request, user: dict = Depends(require_user)):
    return templates.TemplateResponse(
        request, "dashboard/learning_path.html", _ctx(user, active="learning-path")
    )


@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, user: dict = Depends(require_user)):
    history = history_service.get_user_history(user["UserID"])
    bookmarks = bookmark_service.list(user["UserID"])
    return templates.TemplateResponse(
        request,
        "dashboard/history.html",
        _ctx(user, history=history, bookmarks=bookmarks, active="history"),
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, user: dict = Depends(require_user)):
    stats = analytics_service.get_stats(user["UserID"])
    return templates.TemplateResponse(
        request, "dashboard/profile.html", _ctx(user, stats=stats, active="profile")
    )


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, user: dict = Depends(require_user)):
    settings = settings_service.get(user["UserID"])
    return templates.TemplateResponse(
        request, "dashboard/settings.html", _ctx(user, settings=settings, active="settings")
    )

"""REST API routes for AI features and user actions."""
import json
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import ValidationError

from app.ai.explain_module import explain_module
from app.ai.flashcard_module import flashcard_module
from app.ai.learning_path_module import learning_path_module
from app.ai.qa_module import qa_module
from app.ai.quiz_module import quiz_module
from app.ai.summary_module import summary_module
from app.dependencies import get_current_user_id, require_user
from app.models.schemas import (
    AskRequest,
    BookmarkRequest,
    ExplainRequest,
    FlashcardRequest,
    LearningPathRequest,
    LoginRequest,
    ProfileUpdate,
    QuizRequest,
    SettingsUpdate,
    SignupRequest,
    SummaryRequest,
)
from app.services.analytics_service import analytics_service
from app.services.auth_service import auth_service
from app.services.bookmark_service import bookmark_service
from app.services.history_service import history_service
from app.services.settings_service import settings_service
from app.utils.export_utils import export_quiz_pdf, export_text_pdf
from app.utils.security import create_access_token
from app.utils.markdown_utils import render_markdown
from app.utils.pdf_utils import extract_document_text

router = APIRouter(prefix="/api")


def _set_auth_cookie(response: JSONResponse, token: str, remember: bool = False) -> JSONResponse:
    max_age = 30 * 86400 if remember else 7 * 86400
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=max_age,
        samesite="lax",
    )
    return response


@router.post("/signup")
async def api_signup(body: SignupRequest):
    if body.password != body.confirm_password:
        raise HTTPException(400, "Passwords do not match")
    try:
        user = auth_service.signup(body.username, body.email, body.password)
        token = create_access_token(user["UserID"])
        resp = JSONResponse({"success": True, "user": {"username": user["UserName"], "email": user["Email"]}})
        return _set_auth_cookie(resp, token)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/login")
async def api_login(body: LoginRequest):
    try:
        user, token = auth_service.login(body.email, body.password, body.remember_me)
        resp = JSONResponse({"success": True, "user": {"username": user["UserName"], "email": user["Email"]}})
        return _set_auth_cookie(resp, token, body.remember_me)
    except ValueError as e:
        raise HTTPException(401, str(e))


@router.post("/ask")
async def api_ask(body: AskRequest, user: dict = Depends(require_user)):
    api_key = settings_service.get_api_key(user["UserID"])
    query = history_service.create_query(user["UserID"], "qa", body.question)
    try:
        response, model = await qa_module.answer(
            body.question, user["UserID"], api_key
        )
        history_service.save_response(query["QueryID"], response, model)
        analytics_service.increment(user["UserID"], "QuestionsAsked")
        return {
            "success": True,
            "query_id": query["QueryID"],
            "response": response,
            "html": render_markdown(response),
            "model": model,
        }
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"AI service error: {e}")


@router.post("/ask/stream")
async def api_ask_stream(body: AskRequest, user: dict = Depends(require_user)):
    api_key = settings_service.get_api_key(user["UserID"])
    query = history_service.create_query(user["UserID"], "qa", body.question)

    async def generate():
        full = ""
        try:
            async for chunk in qa_module.stream_answer(
                body.question, user["UserID"], api_key
            ):
                full += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            history_service.save_response(query["QueryID"], full, "Gemini 1.5 Pro")
            analytics_service.increment(user["UserID"], "QuestionsAsked")
            yield f"data: {json.dumps({'done': True, 'query_id': query['QueryID']})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/explain")
async def api_explain(body: ExplainRequest, user: dict = Depends(require_user)):
    query = history_service.create_query(user["UserID"], "explain", body.topic)
    try:
        response, model = await explain_module.explain(body.topic, body.level)
        history_service.save_response(query["QueryID"], response, model)
        analytics_service.increment(user["UserID"], "QuestionsAsked")
        return {
            "success": True,
            "query_id": query["QueryID"],
            "response": response,
            "html": render_markdown(response),
            "model": model,
        }
    except Exception as e:
        raise HTTPException(500, f"Explanation error: {e}")


@router.post("/quiz")
async def api_quiz(body: QuizRequest, user: dict = Depends(require_user)):
    api_key = settings_service.get_api_key(user["UserID"])
    query = history_service.create_query(
        user["UserID"], "quiz", f"{body.topic} ({body.difficulty}, {body.num_questions}Q)"
    )
    try:
        questions, model = await quiz_module.generate(
            body.topic, body.difficulty, body.num_questions, api_key
        )
        history_service.save_quiz_questions(query["QueryID"], questions)
        history_service.save_response(query["QueryID"], json.dumps(questions), model)
        analytics_service.increment(user["UserID"], "QuizzesTaken")
        return {"success": True, "query_id": query["QueryID"], "questions": questions, "model": model}
    except Exception as e:
        raise HTTPException(500, f"Quiz generation error: {e}")


@router.post("/summary")
async def api_summary(body: SummaryRequest, user: dict = Depends(require_user)):
    api_key = settings_service.get_api_key(user["UserID"])
    query = history_service.create_query(user["UserID"], "summarize", body.text[:200])
    try:
        response, model = await summary_module.summarize(body.text, body.summary_type, api_key)
        history_service.save_summary(query["QueryID"], body.text, response, model)
        history_service.save_response(query["QueryID"], response, model)
        analytics_service.increment(user["UserID"], "SummariesCreated")
        return {
            "success": True,
            "query_id": query["QueryID"],
            "response": response,
            "html": render_markdown(response),
            "model": model,
        }
    except Exception as e:
        raise HTTPException(500, f"Summary error: {e}")


@router.post("/learning-path")
async def api_learning_path(body: LearningPathRequest, user: dict = Depends(require_user)):
    api_key = settings_service.get_api_key(user["UserID"])
    query = history_service.create_query(user["UserID"], "learn", body.topic)
    try:
        response, model = await learning_path_module.generate(
            body.topic, body.current_level, body.weekly_hours, body.goal, api_key
        )
        history_service.save_learning_path(query["QueryID"], body.topic, body.current_level, response)
        history_service.save_response(query["QueryID"], response, model)
        analytics_service.increment(user["UserID"], "LearningPaths")
        return {
            "success": True,
            "query_id": query["QueryID"],
            "response": response,
            "html": render_markdown(response),
            "model": model,
        }
    except Exception as e:
        raise HTTPException(500, f"Learning path error: {e}")


@router.post("/upload")
async def api_upload(
    file: UploadFile = File(...),
    user: dict = Depends(require_user),
):
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 10MB)")
    try:
        text = extract_document_text(file.filename, content)
        return {"success": True, "filename": file.filename, "text": text, "length": len(text)}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/flashcards")
async def api_flashcards(body: FlashcardRequest, user: dict = Depends(require_user)):
    api_key = settings_service.get_api_key(user["UserID"])
    cards = await flashcard_module.generate(body.topic, body.num_cards, api_key)
    return {"success": True, "cards": cards}


@router.get("/history")
async def api_history(user: dict = Depends(require_user)):
    return {"history": history_service.get_user_history(user["UserID"])}


@router.get("/history/search")
async def api_search_history(q: str, user: dict = Depends(require_user)):
    return {"results": history_service.search_history(user["UserID"], q)}


@router.delete("/history")
async def api_delete_history(user: dict = Depends(require_user)):
    count = history_service.delete_user_history(user["UserID"])
    return {"success": True, "deleted": count}


@router.post("/bookmarks")
async def api_add_bookmark(body: BookmarkRequest, user: dict = Depends(require_user)):
    bm = bookmark_service.add(user["UserID"], body.query_id, body.title)
    return {"success": True, "bookmark": bm}


@router.delete("/bookmarks/{bookmark_id}")
async def api_remove_bookmark(bookmark_id: str, user: dict = Depends(require_user)):
    bookmark_service.remove(user["UserID"], bookmark_id)
    return {"success": True}


@router.get("/bookmarks")
async def api_bookmarks(user: dict = Depends(require_user)):
    return {"bookmarks": bookmark_service.list(user["UserID"])}


@router.get("/dashboard/stats")
async def api_dashboard_stats(user: dict = Depends(require_user)):
    return analytics_service.get_dashboard_data(user["UserID"])


@router.put("/settings")
async def api_update_settings(body: SettingsUpdate, user: dict = Depends(require_user)):
    updates = body.model_dump(exclude_none=True)
    mapped = {}
    if "dark_mode" in updates:
        mapped["DarkMode"] = updates["dark_mode"]
    if "language" in updates:
        mapped["Language"] = updates["language"]
    if "gemini_api_key" in updates:
        mapped["GeminiAPIKey"] = updates["gemini_api_key"]
    settings = settings_service.update(user["UserID"], **mapped)
    return {"success": True, "settings": settings}


@router.put("/profile")
async def api_update_profile(body: ProfileUpdate, user: dict = Depends(require_user)):
    try:
        updated = auth_service.update_profile(
            user["UserID"],
            username=body.username,
            email=str(body.email) if body.email else None,
        )
        return {"success": True, "user": {"username": updated["UserName"], "email": updated["Email"]}}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/export/quiz")
async def api_export_quiz(user: dict = Depends(require_user)):
  # expects JSON body via request
    raise HTTPException(501, "Use /api/export/quiz-pdf with POST body")


@router.post("/export/quiz-pdf")
async def api_export_quiz_pdf(request: Request, user: dict = Depends(require_user)):
    data = await request.json()
    pdf = export_quiz_pdf(data.get("topic", "Quiz"), data.get("questions", []))
    return StreamingResponse(
        iter([pdf]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=quiz.pdf"},
    )


@router.post("/export/summary-pdf")
async def api_export_summary_pdf(request: Request, user: dict = Depends(require_user)):
    data = await request.json()
    pdf = export_text_pdf(data.get("title", "Summary"), data.get("content", ""))
    return StreamingResponse(
        iter([pdf]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=summary.pdf"},
    )


@router.post("/export/learning-path-pdf")
async def api_export_learning_path_pdf(request: Request, user: dict = Depends(require_user)):
    data = await request.json()
    pdf = export_text_pdf(data.get("title", "Learning Path"), data.get("content", ""))
    return StreamingResponse(
        iter([pdf]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=learning-path.pdf"},
    )

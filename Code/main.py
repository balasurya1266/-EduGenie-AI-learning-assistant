"""EduGenie FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_NAME, DEBUG, STATIC_DIR
from app.models.database import _ensure_collections
from app.routes import api, pages

_ensure_collections()

app = FastAPI(
    title=APP_NAME,
    description="AI-powered educational learning assistant",
    version="1.0.0",
    docs_url="/docs" if DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(pages.router)
app.include_router(api.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if DEBUG:
        return JSONResponse(status_code=500, content={"detail": str(exc)})
    return JSONResponse(status_code=500, content={"detail": "An internal error occurred."})


@app.get("/health")
async def health():
    return {"status": "healthy", "app": APP_NAME}

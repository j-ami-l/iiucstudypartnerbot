"""FastAPI routes for portal API endpoints."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from app import db_stats
from app.config import settings
from app.utils.tokens import hash_token
from portal.auth import (
    SESSION_COOKIE_NAME,
    sign_session_cookie,
)
from portal.deps import get_current_user
from portal.schemas import (
    AskQuestionRequest,
    AskQuestionResponse,
    DashboardResponse,
    HistoryResponse,
    LeaderboardItem,
    MeResponse,
    MistakeItem,
    NoteDetailResponse,
    NotesListResponse,
    OkResponse,
    TokenExchangeRequest,
    WeakTopicItem,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/auth/exchange", response_model=OkResponse)
def auth_exchange(
    payload: TokenExchangeRequest, request: Request, response: Response
):
    """Exchange a single-use magic-link token for a signed session cookie."""
    token_h = hash_token(payload.token.strip())
    telegram_id = db_stats.consume_portal_token_sync(token_h)
    if telegram_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_token"
        )

    cookie_val = sign_session_cookie(telegram_id)
    is_secure = (
        request.url.scheme == "https"
        or request.headers.get("x-forwarded-proto") == "https"
    )

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=cookie_val,
        httponly=True,
        samesite="lax",
        secure=is_secure,
        path="/",
        max_age=settings.PORTAL_SESSION_DAYS * 86400,
    )
    return OkResponse(ok=True)


@router.post("/auth/logout", response_model=OkResponse)
def auth_logout(response: Response):
    """Clear session cookie and log user out."""
    response.delete_cookie(
        key=SESSION_COOKIE_NAME, path="/", httponly=True, samesite="lax"
    )
    return OkResponse(ok=True)


@router.get("/me", response_model=MeResponse)
def get_me(user_id: int = Depends(get_current_user)):
    """Return logged-in user details."""
    info = db_stats.get_user_info_sync(user_id)
    name = info.get("name") if info else None
    language = info.get("language") if info else "en"
    return MeResponse(
        name=name, language=language, bot_username=settings.BOT_USERNAME
    )


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(user_id: int = Depends(get_current_user)):
    """Return overview metrics and recent notes for student dashboard."""
    stats = db_stats.get_dashboard_stats_sync(user_id)
    return DashboardResponse(**stats)


@router.get("/notes", response_model=NotesListResponse)
def get_notes(
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    user_id: int = Depends(get_current_user),
):
    """Return paginated list of notes for logged-in user."""
    items, total = db_stats.get_user_notes_sync(user_id, limit=limit, offset=offset)
    return NotesListResponse(items=items, total=total)


@router.get("/notes/{note_id}", response_model=NoteDetailResponse)
def get_note_detail(note_id: int, user_id: int = Depends(get_current_user)):
    """Return complete note details. Returns 404 if not found or belongs to another user."""
    note = db_stats.get_user_note_detail_sync(user_id, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="note_not_found"
        )
    return NoteDetailResponse(**note)


@router.get("/weak-topics", response_model=List[WeakTopicItem])
def get_weak_topics_route(user_id: int = Depends(get_current_user)):
    """Return list of weak topics ordered worst accuracy first."""
    topics = db_stats.get_weak_topics_sync(user_id)
    return [WeakTopicItem(**t) for t in topics]


@router.get("/mistakes", response_model=List[MistakeItem])
def get_mistakes_route(user_id: int = Depends(get_current_user)):
    """Return current mistake notebook."""
    mistakes = db_stats.get_mistakes_sync(user_id)
    return [MistakeItem(**m) for m in mistakes]


@router.get("/history", response_model=HistoryResponse)
def get_history(user_id: int = Depends(get_current_user)):
    """Return past quiz attempts and 6-week accuracy trend."""
    data = db_stats.get_history_stats_sync(user_id)
    return HistoryResponse(**data)


@router.get("/leaderboard", response_model=List[LeaderboardItem])
def get_leaderboard(user_id: int = Depends(get_current_user)):
    """Return weekly campus leaderboard ranking top active students."""
    board = db_stats.get_leaderboard_sync(user_id)
    return [LeaderboardItem(**b) for b in board]


@router.post("/notes/{note_id}/ask", response_model=AskQuestionResponse)
async def ask_ai_tutor(
    note_id: int,
    payload: AskQuestionRequest,
    user_id: int = Depends(get_current_user),
):
    """Ask Gemma AI tutor an interactive question about a study note."""
    note = db_stats.get_user_note_detail_sync(user_id, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="note_not_found"
        )

    from app.ai.gemma_client import GemmaClient

    title = note.get("title") or f"Study Note #{note_id}"
    summary = note.get("summary_text") or ""
    system_prompt = (
        "You are SnapStudy AI, an expert, encouraging university study tutor. "
        f"The student is asking a question about their study note titled '{title}'.\n"
        f"Context from study note:\n{summary}\n\n"
        "Instructions:\n"
        "- Answer the student's question clearly, accurately, and concisely based on the study note.\n"
        "- Use bullet points, bold key terms, and simple real-world analogies where helpful.\n"
        "- If the note does not contain enough info, provide a helpful general explanation while mentioning that.\n"
        "- Keep the tone positive and academic. Respond in the same language as the question (English or Bengali)."
    )

    client = GemmaClient()
    answer = await client.generate(system_prompt, payload.question.strip())
    return AskQuestionResponse(answer=answer)


import math
from fastapi import APIRouter, Request, Query, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from data.database import get_db
from data.models import LoadPattern, PatternLike, PatternStatus, User
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_current_user_id(db: Session) -> int:
    user = db.query(User).first()
    if not user:
        raise Exception("В БД нет пользователей! Выполните: python3 init_data.py")
    return user.id


@router.get("/")
def root():
    return RedirectResponse(url="/load_patterns")


@router.get("/load_patterns")
def get_patterns_grid(
    request: Request,
    max_expected: int = Query(default=None, description="Фильтр по матожиданию"),
    db: Session = Depends(get_db)
):
    query = db.query(LoadPattern).filter(LoadPattern.status == PatternStatus.published)

    if max_expected is not None:
        max_expected_full = max_expected * 1000000
        query = query.filter(LoadPattern.expected_request_count <= max_expected_full)

    patterns = query.all()

    for pattern in patterns:
        pattern.likes_count = db.query(PatternLike).filter(
            PatternLike.pattern_id == pattern.id
        ).count()

    return templates.TemplateResponse(
        request=request,
        name="patterns.html",
        context={
            "patterns": patterns,
            "max_expected": max_expected * 1000000 if max_expected else None
        },
    )


# ВАЖНО: статические пути (/draft, /lenta) регистрируются
# ДО динамического /{pattern_id}, иначе FastAPI матчит их как pattern_id и падает с 422.

@router.get("/load_patterns/draft")
def get_forecast_form(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user_id = get_current_user_id(db)

    draft = db.query(LoadPattern).filter(
        LoadPattern.creator_id == current_user_id,
        LoadPattern.status == PatternStatus.draft
    ).first()

    forecast = None
    if draft and draft.requests_per_second:
        rps = draft.requests_per_second or 0
        multiplier = draft.peak_multiplier or 1.0
        effective_rps = rps * multiplier
        required_cpu = math.ceil(effective_rps / 200)
        required_ram = math.ceil(effective_rps / 500)
        forecast = {
            "effective_rps": effective_rps,
            "required_cpu": required_cpu,
            "required_ram": required_ram,
        }

    return templates.TemplateResponse(
        request=request,
        name="forecast_form.html",
        context={"draft": draft, "forecast": forecast},
    )


@router.get("/load_patterns/lenta")
def lenta_entry(db: Session = Depends(get_db)):
    """
    Точка входа в ленту без хардкода ID=1.
    Находит первый опубликованный паттерн через SQL (ORDER BY id LIMIT 1)
    и редиректит на него. Так лента работает даже если ID начинаются не с 1
    (из-за пропусков/сброса последовательности в Postgres).
    """
    first = db.query(LoadPattern).filter(
        LoadPattern.status == PatternStatus.published
    ).order_by(LoadPattern.id).first()

    if not first:
        raise HTTPException(status_code=404, detail="Нет опубликованных паттернов")

    return RedirectResponse(url=f"/load_patterns/{first.id}")


@router.post("/load_patterns/draft/create")
def create_draft(
    request: Request,
    pattern_name: str = Form(...),
    image_filename: Optional[str] = Form(None),
    video_filename: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    current_user_id = get_current_user_id(db)

    existing_draft = db.query(LoadPattern).filter(
        LoadPattern.creator_id == current_user_id,
        LoadPattern.status == PatternStatus.draft
    ).first()

    if not existing_draft:
        image_url = f"/invalid-upload/{image_filename}" if image_filename else None
        video_url = f"/invalid-upload/{video_filename}" if video_filename else None

        new_draft = LoadPattern(
            pattern_name=pattern_name,
            pattern_code=pattern_name.lower().replace(" ", "_").replace("-", "_"),
            status=PatternStatus.draft,
            creator_id=current_user_id,
            image_url=image_url,
            video_url=video_url
        )
        db.add(new_draft)
        db.commit()

    return RedirectResponse(url="/load_patterns/draft", status_code=303)


@router.post("/load_patterns/draft/publish")
def publish_draft(
    request: Request,
    requests_per_second: int = Form(...),
    peak_multiplier: float = Form(...),
    duration_hours: int = Form(...),
    description: str = Form(default=""),
    db: Session = Depends(get_db)
):
    current_user_id = get_current_user_id(db)

    draft = db.query(LoadPattern).filter(
        LoadPattern.creator_id == current_user_id,
        LoadPattern.status == PatternStatus.draft
    ).first()

    if draft:
        draft.requests_per_second = requests_per_second
        draft.peak_multiplier = peak_multiplier
        draft.duration_hours = duration_hours
        draft.description = description
        draft.expected_request_count = int(requests_per_second * peak_multiplier * duration_hours * 3600)
        draft.average_request_count = requests_per_second
        draft.status = PatternStatus.published
        db.commit()

    return RedirectResponse(url="/load_patterns", status_code=303)


@router.get("/load_patterns/{pattern_id}")
def get_pattern_detail(
    request: Request,
    pattern_id: int,
    next: bool = Query(default=False),
    db: Session = Depends(get_db)
):
    if next:
        pattern = db.query(LoadPattern).filter(
            LoadPattern.status == PatternStatus.published,
            LoadPattern.id > pattern_id
        ).order_by(LoadPattern.id).first()

        if not pattern:
            pattern = db.query(LoadPattern).filter(
                LoadPattern.status == PatternStatus.published
            ).order_by(LoadPattern.id).first()

        if not pattern:
            raise HTTPException(status_code=404, detail="Нет опубликованных паттернов")
    else:
        pattern = db.query(LoadPattern).filter(
            LoadPattern.id == pattern_id,
            LoadPattern.status == PatternStatus.published
        ).first()

        if not pattern:
            raise HTTPException(status_code=404, detail="Паттерн не найден или удалён")

    pattern.likes_count = db.query(PatternLike).filter(
        PatternLike.pattern_id == pattern.id
    ).count()

    return templates.TemplateResponse(
        request=request,
        name="pattern_detail.html",
        context={"pattern": pattern},
    )


@router.post("/load_patterns/{pattern_id}/delete")
def delete_pattern(
    pattern_id: int,
    db: Session = Depends(get_db)
):
    sql = text("UPDATE load_patterns SET status = 'deleted' WHERE id = :pattern_id")
    db.execute(sql, {"pattern_id": pattern_id})
    db.commit()

    return RedirectResponse(url="/load_patterns", status_code=303)

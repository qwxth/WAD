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
    """Получить ID первого пользователя из БД"""
    user = db.query(User).first()
    if not user:
        raise Exception("В БД нет пользователей! Выполните: python3 init_data.py")
    return user.id


@router.get("/")
def root():
    return RedirectResponse(url="/patterns")


@router.get("/patterns")
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


@router.get("/pattern/{pattern_id}")
def get_pattern_detail(
    request: Request,
    pattern_id: int,
    next: bool = Query(default=False),
    db: Session = Depends(get_db)
):
    visible = db.query(LoadPattern).filter(
        LoadPattern.status == PatternStatus.published
    ).all()
    
    if not visible:
        raise HTTPException(status_code=404, detail="Нет опубликованных паттернов")
    
    if next:
        current_index = None
        for i, p in enumerate(visible):
            if p.id == pattern_id:
                current_index = i
                break
        if current_index is not None and current_index + 1 < len(visible):
            pattern = visible[current_index + 1]
        else:
            pattern = visible[0]
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


@router.get("/forecast")
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


@router.post("/forecast/create")
def create_draft(
    request: Request,
    pattern_name: str = Form(...),
    image_url: Optional[str] = Form(None),
    video_url: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    current_user_id = get_current_user_id(db)
    
    existing_draft = db.query(LoadPattern).filter(
        LoadPattern.creator_id == current_user_id,
        LoadPattern.status == PatternStatus.draft
    ).first()
    
    if not existing_draft:
        new_draft = LoadPattern(
            pattern_name=pattern_name,
            pattern_code=pattern_name.lower().replace(" ", "_").replace("-", "_"),
            status=PatternStatus.draft,
            creator_id=current_user_id,
            image_url=image_url if image_url else None,
            video_url=video_url if video_url else None
        )
        db.add(new_draft)
        db.commit()
    
    return RedirectResponse(url="/forecast", status_code=303)


@router.post("/forecast/publish")
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
    
    return RedirectResponse(url="/patterns", status_code=303)


@router.post("/pattern/{pattern_id}/delete")
def delete_pattern(
    pattern_id: int,
    db: Session = Depends(get_db)
):
    sql = text("UPDATE load_patterns SET status = 'deleted' WHERE id = :pattern_id")
    db.execute(sql, {"pattern_id": pattern_id})
    db.commit()
    
    return RedirectResponse(url="/patterns", status_code=303)

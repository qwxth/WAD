from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import Optional
from data.database import get_db
from data.models import LoadPattern, PatternLike, PatternStatus, User
from data.minio_client import upload_file, generate_latin_filename
from api.schemas import (
    PatternResponse, PatternListResponse, PatternPublishRequest,
    LikeRequest, MessageResponse
)
from api.auth import get_current_user

router = APIRouter(prefix="/api/patterns", tags=["patterns"])


def _enrich_pattern(pattern: LoadPattern, db: Session, current_user: User) -> dict:
    """
    Сериализация модели LoadPattern -> PatternResponse.
    Добавляет вычисляемые поля is_owner, is_liked, likes_count,
    которые не хранятся в БД напрямую, а вычисляются на лету.
    """
    likes_count = db.query(PatternLike).filter(PatternLike.pattern_id == pattern.id).count()
    is_liked = db.query(PatternLike).filter(
        PatternLike.pattern_id == pattern.id,
        PatternLike.user_id == current_user.id
    ).first() is not None
    return {
        "id": pattern.id,
        "pattern_name": pattern.pattern_name,
        "pattern_code": pattern.pattern_code,
        "status": pattern.status.value,
        "expected_request_count": pattern.expected_request_count,
        "average_request_count": pattern.average_request_count,
        "requests_per_second": pattern.requests_per_second,
        "peak_multiplier": pattern.peak_multiplier,
        "duration_hours": pattern.duration_hours,
        "description": pattern.description,
        "use_case": pattern.use_case,
        "image_url": pattern.image_url,
        "video_url": pattern.video_url,
        "base_cpu_cores": pattern.base_cpu_cores,
        "base_ram_gb": pattern.base_ram_gb,
        "created_at": pattern.created_at,
        "creator_id": pattern.creator_id,
        "likes_count": likes_count,
        "is_owner": 1 if pattern.creator_id == current_user.id else 0,
        "is_liked": 1 if is_liked else 0,
    }


# ========== GET список (с фильтрацией) ==========
# Признак is_owner: 0/1 если создатель услуги совпадает с текущим пользователем
@router.get("", response_model=PatternListResponse)
def list_patterns(
    max_expected: Optional[int] = Query(None, description="Макс. матожидание (млн)"),
    min_rps: Optional[int] = Query(None, description="Мин. RPS"),
    max_rps: Optional[int] = Query(None, description="Макс. RPS"),
    search: Optional[str] = Query(None, description="Поиск по названию"),
    db: Session = Depends(get_db),
):
    current_user = get_current_user(db)  # singleton-функция
    query = db.query(LoadPattern).filter(LoadPattern.status == PatternStatus.published)

    if max_expected is not None:
        query = query.filter(LoadPattern.expected_request_count <= max_expected * 1_000_000)
    if min_rps is not None:
        query = query.filter(LoadPattern.requests_per_second >= min_rps)
    if max_rps is not None:
        query = query.filter(LoadPattern.requests_per_second <= max_rps)
    if search:
        query = query.filter(LoadPattern.pattern_name.ilike(f"%{search}%"))

    patterns = query.order_by(LoadPattern.id).all()
    items = [_enrich_pattern(p, db, current_user) for p in patterns]
    return {"items": items, "total": len(items)}


# ========== GET лента без ID (признак is_liked) ==========
@router.get("/feed", response_model=PatternListResponse)
def feed_patterns(db: Session = Depends(get_db)):
    current_user = get_current_user(db)
    patterns = db.query(LoadPattern).filter(
        LoadPattern.status == PatternStatus.published
    ).order_by(LoadPattern.id).all()
    items = [_enrich_pattern(p, db, current_user) for p in patterns]
    return {"items": items, "total": len(items)}


# ========== GET черновик (не более 1, без ID) ==========
@router.get("/draft", response_model=PatternResponse)
def get_draft(db: Session = Depends(get_db)):
    current_user = get_current_user(db)
    draft = db.query(LoadPattern).filter(
        LoadPattern.creator_id == current_user.id,
        LoadPattern.status == PatternStatus.draft
    ).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Черновик не найден")
    return _enrich_pattern(draft, db, current_user)


# ========== GET лента по ID (?next=true — получить следующую карточку) ==========
@router.get("/{pattern_id}", response_model=PatternResponse)
def get_pattern(
    pattern_id: int,
    next: bool = Query(default=False, description="Если true — вернуть следующий паттерн в ленте"),
    db: Session = Depends(get_db),
):
    current_user = get_current_user(db)

    if next:
        # Логика "следующая карточка в ленте" (как свайп в Reels)
        visible = db.query(LoadPattern).filter(
            LoadPattern.status == PatternStatus.published
        ).order_by(LoadPattern.id).all()

        if not visible:
            raise HTTPException(status_code=404, detail="Нет опубликованных паттернов")

        current_index = None
        for i, p in enumerate(visible):
            if p.id == pattern_id:
                current_index = i
                break

        if current_index is not None and current_index + 1 < len(visible):
            pattern = visible[current_index + 1]
        else:
            pattern = visible[0]  # зацикливаем ленту

        return _enrich_pattern(pattern, db, current_user)

    # Обычное получение паттерна по ID
    pattern = db.query(LoadPattern).filter(
        LoadPattern.id == pattern_id,
        LoadPattern.status != PatternStatus.deleted
    ).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="Паттерн не найден")
    if pattern.status == PatternStatus.draft and pattern.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к чужому черновику")
    return _enrich_pattern(pattern, db, current_user)


# ========== POST создание (с файлами image+video) ==========
# Системные поля (id, status, creator_id, created_at) с клиента НЕ принимаются —
# они вычисляются на бэкенде через get_current_user() и бизнес-логику.
@router.post("", response_model=PatternResponse, status_code=201)
async def create_pattern(
    pattern_name: str = Form(...),
    description: Optional[str] = Form(None),
    use_case: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    current_user = get_current_user(db)  # singleton - определяет создателя

    existing = db.query(LoadPattern).filter(
        LoadPattern.creator_id == current_user.id,
        LoadPattern.status == PatternStatus.draft
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="У вас уже есть черновик. Опубликуйте или удалите его.")

    image_url = None
    video_url = None

    if image and image.filename:
        img_bytes = await image.read()
        fname = generate_latin_filename(image.filename)  # латинское имя
        image_url = upload_file(img_bytes, fname, image.content_type or "image/jpeg")

    if video and video.filename:
        vid_bytes = await video.read()
        fname = generate_latin_filename(video.filename)
        video_url = upload_file(vid_bytes, fname, video.content_type or "video/mp4")

    pattern_code = pattern_name.lower().replace(" ", "_").replace("-", "_")
    pattern_code = "".join(c for c in pattern_code if c.isascii())[:50] or "pattern"

    new_pattern = LoadPattern(
        pattern_name=pattern_name,
        pattern_code=pattern_code,
        status=PatternStatus.draft,       # системное поле - только draft при создании
        creator_id=current_user.id,       # системное поле - из singleton, не от клиента
        description=description,
        use_case=use_case,
        image_url=image_url,
        video_url=video_url,
    )
    db.add(new_pattern)
    db.commit()
    db.refresh(new_pattern)
    return _enrich_pattern(new_pattern, db, current_user)


# ========== PUT публикация (смена статуса draft -> published, НАЗАД НЕЛЬЗЯ) ==========
@router.put("/{pattern_id}/publish", response_model=PatternResponse)
def publish_pattern(
    pattern_id: int,
    data: PatternPublishRequest,
    db: Session = Depends(get_db),
):
    current_user = get_current_user(db)
    pattern = db.query(LoadPattern).filter(LoadPattern.id == pattern_id).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="Паттерн не найден")
    if pattern.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец может публиковать")
    if pattern.status != PatternStatus.draft:
        # Бизнес-правило: публиковать можно ТОЛЬКО из draft. Опубликованное нельзя снова "опубликовать".
        raise HTTPException(status_code=400, detail="Публиковать можно только черновики")

    if data.pattern_name:
        pattern.pattern_name = data.pattern_name
    pattern.requests_per_second = data.requests_per_second
    pattern.peak_multiplier = data.peak_multiplier
    pattern.duration_hours = data.duration_hours
    pattern.description = data.description or pattern.description
    pattern.use_case = data.use_case or pattern.use_case
    pattern.base_cpu_cores = data.base_cpu_cores
    pattern.base_ram_gb = data.base_ram_gb
    pattern.expected_request_count = int(
        data.requests_per_second * data.peak_multiplier * data.duration_hours * 3600
    )
    pattern.average_request_count = data.requests_per_second
    pattern.status = PatternStatus.published  # системное поле - вычисляется, не от клиента

    db.commit()
    db.refresh(pattern)
    return _enrich_pattern(pattern, db, current_user)


# ========== DELETE (soft delete, только свои, НАЗАД В DRAFT НЕЛЬЗЯ) ==========
@router.delete("/{pattern_id}", response_model=MessageResponse)
def delete_pattern(pattern_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(db)
    pattern = db.query(LoadPattern).filter(LoadPattern.id == pattern_id).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="Паттерн не найден")
    if pattern.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Удалять можно только свои паттерны")
    if pattern.status == PatternStatus.deleted:
        raise HTTPException(status_code=400, detail="Паттерн уже удалён")

    pattern.status = PatternStatus.deleted  # soft delete - запись остаётся в БД
    db.commit()
    return {"message": f"Паттерн {pattern_id} удалён (soft delete)"}


# ========== POST лайк (0/1 от текущего пользователя) ==========
@router.post("/{pattern_id}/like", response_model=MessageResponse)
def like_pattern(pattern_id: int, data: LikeRequest, db: Session = Depends(get_db)):
    current_user = get_current_user(db)  # singleton
    pattern = db.query(LoadPattern).filter(
        LoadPattern.id == pattern_id,
        LoadPattern.status == PatternStatus.published
    ).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="Паттерн не найден или не опубликован")

    existing_like = db.query(PatternLike).filter(
        PatternLike.pattern_id == pattern_id,
        PatternLike.user_id == current_user.id
    ).first()

    if data.value == 1:
        if existing_like:
            return {"message": "Лайк уже стоит"}
        new_like = PatternLike(user_id=current_user.id, pattern_id=pattern_id)
        db.add(new_like)
        db.commit()
        return {"message": "Лайк поставлен"}
    else:
        if existing_like:
            db.delete(existing_like)
            db.commit()
            return {"message": "Лайк убран"}
        return {"message": "Лайка и не было"}

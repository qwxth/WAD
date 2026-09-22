import math
from fastapi import APIRouter, Request, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from data.collections import server_load_patterns_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _visible_patterns():
    return [p for p in server_load_patterns_db if p["status"] == "published"]


def _draft_pattern():
    for p in server_load_patterns_db:
        if p["status"] == "draft":
            return p
    return None


@router.get("/")
def root():
    return RedirectResponse(url="/patterns")


@router.get("/patterns")
def get_patterns_grid(
    request: Request,
    max_expected: int = Query(default=None, description="Фильтр по матожиданию"),
):
    patterns = _visible_patterns()
    if max_expected is not None:
        max_expected_full = max_expected * 1000000
        patterns = [p for p in patterns if p["expected_request_count"] <= max_expected_full]
    for p in patterns:
        p["likes_count"] = len(p["likes"])
    return templates.TemplateResponse(
        request=request,
        name="patterns.html",
        context={"patterns": patterns, "max_expected": max_expected * 1000000 if max_expected else None},
    )


@router.get("/pattern/{pattern_id}")
def get_pattern_detail(
    request: Request,
    pattern_id: int,
    next: bool = Query(default=False),
):
    visible = _visible_patterns()
    if next:
        current_index = None
        for i, p in enumerate(visible):
            if p["id"] == pattern_id:
                current_index = i
                break
        if current_index is not None and current_index + 1 < len(visible):
            pattern = visible[current_index + 1]
        else:
            pattern = visible[0] if visible else None
    else:
        pattern = None
        for p in visible:
            if p["id"] == pattern_id:
                pattern = p
                break
    if pattern:
        pattern["likes_count"] = len(pattern["likes"])
    return templates.TemplateResponse(
        request=request,
        name="pattern_detail.html",
        context={"pattern": pattern},
    )


@router.get("/forecast")
def get_forecast_form(request: Request):
    draft = _draft_pattern()
    forecast = None
    if draft:
        rps = draft["requests_per_second"]
        multiplier = draft["peak_multiplier"]
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

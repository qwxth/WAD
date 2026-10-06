from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ========== USER ==========
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== PATTERN ==========
class PatternPublishRequest(BaseModel):
    pattern_name: Optional[str] = None
    requests_per_second: int = Field(..., gt=0)
    peak_multiplier: float = Field(..., gt=0)
    duration_hours: int = Field(..., gt=0)
    description: Optional[str] = ""
    use_case: Optional[str] = None
    base_cpu_cores: Optional[int] = None
    base_ram_gb: Optional[int] = None


class PatternResponse(BaseModel):
    id: int
    pattern_name: str
    pattern_code: str
    status: str
    expected_request_count: Optional[int]
    average_request_count: Optional[int]
    requests_per_second: Optional[int]
    peak_multiplier: Optional[float]
    duration_hours: Optional[int]
    description: Optional[str]
    use_case: Optional[str]
    image_url: Optional[str]
    video_url: Optional[str]
    base_cpu_cores: Optional[int]
    base_ram_gb: Optional[int]
    created_at: datetime
    creator_id: int
    likes_count: int = 0
    is_owner: int = 0
    is_liked: int = 0

    class Config:
        from_attributes = True


class PatternListResponse(BaseModel):
    items: List[PatternResponse]
    total: int


class LikeRequest(BaseModel):
    value: int = Field(..., ge=0, le=1)


class MessageResponse(BaseModel):
    message: str

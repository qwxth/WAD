from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class PatternStatus(enum.Enum):
    draft = "draft"
    published = "published"
    deleted = "deleted"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patterns = relationship("LoadPattern", back_populates="creator")
    likes = relationship("PatternLike", back_populates="user")


class LoadPattern(Base):
    __tablename__ = "load_patterns"

    id = Column(Integer, primary_key=True, index=True)
    pattern_name = Column(String(100), nullable=False)
    pattern_code = Column(String(50), nullable=False)
    status = Column(SQLEnum(PatternStatus), default=PatternStatus.draft, nullable=False)

    expected_request_count = Column(Integer, nullable=True)
    average_request_count = Column(Integer, nullable=True)

    requests_per_second = Column(Integer, nullable=True)
    peak_multiplier = Column(Float, nullable=True)
    duration_hours = Column(Integer, nullable=True)

    description = Column(Text, nullable=True)
    use_case = Column(String(200), nullable=True)

    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)

    base_cpu_cores = Column(Integer, nullable=True)
    base_ram_gb = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    creator = relationship("User", back_populates="patterns")
    likes = relationship("PatternLike", back_populates="pattern")


class PatternLike(Base):
    __tablename__ = "pattern_likes"
    __table_args__ = (UniqueConstraint('user_id', 'pattern_id', name='uq_user_pattern_like'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pattern_id = Column(Integer, ForeignKey("load_patterns.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="likes")
    pattern = relationship("LoadPattern", back_populates="likes")

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    settings: Optional[dict] = None


class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    settings: Optional[dict] = None
    created_at: datetime
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PaperBase(BaseModel):
    title: str
    authors: Optional[List[str]] = []
    abstract: Optional[str] = None
    doi: Optional[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None


class PaperCreate(PaperBase):
    pass


class PaperUpdate(BaseModel):
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    reading_progress: Optional[int] = None
    last_read_page: Optional[int] = None


class PaperResponse(PaperBase):
    id: UUID
    user_id: UUID
    pdf_url: Optional[str] = None
    page_count: Optional[int] = None
    status: str
    reading_progress: int
    last_read_page: int
    tags: List[str]
    ai_summary: Optional[str] = None
    ai_keywords: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


class PaperListResponse(BaseModel):
    items: List[PaperResponse]
    total: int
    page: int
    limit: int


class AnnotationPosition(BaseModel):
    type: str
    startOffset: Optional[int] = None
    endOffset: Optional[int] = None
    boundingBox: Optional[List[float]] = None


class AnnotationCreate(BaseModel):
    paper_id: UUID
    type: str
    page: int
    position: AnnotationPosition
    content: Optional[str] = None
    color: Optional[str] = "#FFEB3B"


class AnnotationUpdate(BaseModel):
    content: Optional[str] = None
    color: Optional[str] = None


class AnnotationResponse(AnnotationCreate):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


class CardCreate(BaseModel):
    paper_id: UUID
    question: str
    answer: str
    order: int


class CardUpdate(BaseModel):
    answer: Optional[str] = None


class CardResponse(CardCreate):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


class AIExplainRequest(BaseModel):
    paper_id: UUID
    text: str
    context: Optional[str] = None


class AIExplainResponse(BaseModel):
    explanation: str
    related_concepts: Optional[List[str]] = None


class AIQARequest(BaseModel):
    paper_id: UUID
    question: str


class AIQAResponse(BaseModel):
    answer: str
    source: Optional[dict] = None

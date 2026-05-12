from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON, Text


# ==================== 用户相关 ====================

class UserBase(SQLModel):
    email: str
    name: str


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str
    avatar: Optional[str] = None
    research_interests: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    theme: str = "light"
    daily_push_enabled: bool = True
    push_time: str = "09:00"
    push_channel: str = "app"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(UserBase):
    password: str


class UserLogin(SQLModel):
    email: str
    password: str


class UserRead(UserBase):
    id: int
    avatar: Optional[str]
    research_interests: Optional[List[str]]
    theme: str
    created_at: datetime


# ==================== 文件夹 ====================

class FolderBase(SQLModel):
    name: str
    parent_id: Optional[int] = None


class Folder(FolderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FolderCreate(FolderBase):
    pass


class FolderRead(FolderBase):
    id: int
    user_id: int
    created_at: datetime


# ==================== 标签 ====================

class TagBase(SQLModel):
    name: str
    color: Optional[str] = None


class Tag(TagBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    id: int


# ==================== 论文 ====================

class PaperBase(SQLModel):
    title: str
    authors: List[str]
    year: Optional[int] = None
    venue: Optional[str] = None
    abstract: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None


class Paper(PaperBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    folder_id: Optional[int] = Field(default=None, foreign_key="folder.id")
    authors: List[str] = Field(sa_column=Column(JSON))
    pdf_url: Optional[str] = None
    status: str = "unread"  # unread, reading, completed
    progress: int = 0
    current_page: int = 1
    total_pages: Optional[int] = None
    last_read_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PaperCreate(PaperBase):
    folder_id: Optional[int] = None


class PaperUpdate(SQLModel):
    folder_id: Optional[int] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    current_page: Optional[int] = None


class PaperRead(PaperBase):
    id: int
    user_id: int
    folder_id: Optional[int]
    pdf_url: Optional[str]
    status: str
    progress: int
    current_page: int
    total_pages: Optional[int]
    last_read_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


# ==================== 批注 ====================

class AnnotationBase(SQLModel):
    page: int
    position: dict
    type: str  # highlight, note, underline
    color: Optional[str] = None
    content: Optional[str] = None


class Annotation(AnnotationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    paper_id: int = Field(foreign_key="paper.id")
    user_id: int = Field(foreign_key="user.id")
    position: dict = Field(sa_column=Column(JSON))
    content: Optional[str] = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AnnotationCreate(AnnotationBase):
    pass


class AnnotationRead(AnnotationBase):
    id: int
    paper_id: int
    user_id: int
    created_at: datetime


# ==================== 书签 ====================

class BookmarkBase(SQLModel):
    page: int
    title: Optional[str] = None


class Bookmark(BookmarkBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    paper_id: int = Field(foreign_key="paper.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BookmarkCreate(BookmarkBase):
    pass


class BookmarkRead(BookmarkBase):
    id: int
    paper_id: int
    user_id: int
    created_at: datetime


# ==================== 知识卡片 ====================

class CardBase(SQLModel):
    title: str
    type: str  # concept, method, formula, data
    content: str
    paper_id: Optional[int] = None


class Card(CardBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    content: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CardCreate(CardBase):
    tags: Optional[List[str]] = []


class CardRead(CardBase):
    id: int
    user_id: int
    created_at: datetime


# ==================== AI 对话 ====================

class AIConversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    paper_id: int = Field(foreign_key="paper.id")
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AIMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="aiconversation.id")
    role: str  # user, assistant
    content: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AIChatRequest(SQLModel):
    paper_id: int
    question: str
    conversation_id: Optional[int] = None


class AIChatResponse(SQLModel):
    answer: str
    conversation_id: int
    references: Optional[List[dict]] = None


# ==================== 文献综述 ====================

class ReviewBase(SQLModel):
    topic: str
    paper_ids: List[int]


class Review(ReviewBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    paper_ids: List[int] = Field(sa_column=Column(JSON))
    status: str = "draft"
    content: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReviewCreate(ReviewBase):
    sections: Optional[List[str]] = ["background", "methods", "progress", "comparison", "future"]


class ReviewRead(ReviewBase):
    id: int
    user_id: int
    status: str
    content: Optional[dict]
    created_at: datetime


# ==================== 团队 ====================

class TeamBase(SQLModel):
    name: str
    description: Optional[str] = None


class Team(TeamBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TeamMember(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="team.id")
    user_id: int = Field(foreign_key="user.id")
    role: str = "member"  # admin, member
    joined_at: datetime = Field(default_factory=datetime.utcnow)


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    id: int
    owner_id: int
    created_at: datetime


# ==================== 讨论 ====================

class DiscussionBase(SQLModel):
    title: str
    content: str


class Discussion(DiscussionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="team.id")
    paper_id: Optional[int] = Field(default=None, foreign_key="paper.id")
    user_id: int = Field(foreign_key="user.id")
    content: str = Field(sa_column=Column(Text))
    is_pinned: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DiscussionReply(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    discussion_id: int = Field(foreign_key="discussion.id")
    user_id: int = Field(foreign_key="user.id")
    content: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== 期刊 ====================

class JournalBase(SQLModel):
    name: str
    type: str  # journal, conference
    field: Optional[str] = None
    impact_factor: Optional[float] = None
    deadline: Optional[str] = None
    acceptance_rate: Optional[str] = None
    review_time: Optional[str] = None


class Journal(JournalBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    status: str = "interested"  # interested, targeting, submitted, accepted
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class JournalCreate(JournalBase):
    status: Optional[str] = "interested"


class JournalRead(JournalBase):
    id: int
    user_id: int
    status: str
    created_at: datetime


# ==================== 阅读统计 ====================

class ReadingStats(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    date: str  # YYYY-MM-DD
    papers_read: int = 0
    reading_time: int = 0  # minutes
    annotations: int = 0
    cards_created: int = 0


class StatsOverview(SQLModel):
    papers_read: int
    reading_time: int
    annotations: int
    field_distribution: List[dict]
    keyword_cloud: List[dict]


# ==================== 每日推送 ====================

class DailyRecommendation(SQLModel):
    id: int
    title: str
    authors: str
    year: int
    venue: Optional[str]
    reason: str
    relevance: int


class DailySettings(SQLModel):
    enabled: bool
    time: str
    channel: str
    count: int = 5


class DailyInterests(SQLModel):
    interests: List[str]

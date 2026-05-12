from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from app.core.config import settings

# 导入所有模型以便创建表
from app.models import User, Folder, Tag, Paper, Annotation, Bookmark, Card
from app.models import AIConversation, AIMessage, Review
from app.models import Team, TeamMember, Discussion, DiscussionReply
from app.models import Journal, ReadingStats

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_db_and_tables():
    """创建数据库和表"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

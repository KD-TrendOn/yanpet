from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession,async_sessionmaker, async_scoped_session
import os
from asyncio import current_task
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/mydatabase")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False,)
def get_scoped_session():
        session = async_scoped_session(
            session_factory=async_session,
            scopefunc=current_task,
        )
        return session
async def scoped_session_dependency() -> AsyncSession:
        session = get_scoped_session()
        yield session
        await session.close()


async def init_db():
    async with engine.begin() as conn:
        from models import Question
        from models import Answer
        from models import Base
        await conn.run_sync(Base.metadata.create_all)

"""Criação do engine e da fábrica de sessões assíncronas do SQLAlchemy."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.config.settings import get_settings


def criar_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(
        str(settings.database_url),
        echo=settings.db_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
    )


engine: AsyncEngine = criar_engine()

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Fornece uma sessão por requisição, com commit/rollback automáticos."""
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

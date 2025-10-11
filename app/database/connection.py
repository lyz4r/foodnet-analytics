from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config.settings import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.DATABASE_URL,  # берём строку подключения из настроек (.env)
    echo=False,             # Можно сделать True для детального логирования запросов
    pool_size=10,
    max_overflow=20,
    future=True,
)


async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    """
    Функция-генератор для получения асинхронной сессии базы данных.

    Ничего не принимает, возвращает сессию.

    Пример использования:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            Запрос к БД, работа с моделями
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

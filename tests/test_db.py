import pytest
from app.database.connection import async_session, Base, engine
from app.models.models import User
from sqlalchemy import select


@pytest.mark.asyncio
async def test_db_connection_and_user_crud():
    """Тест на подключение к БД и базовые операции CRUD для модели User.
    !!! Тесты должны быть асинхронными, через пакет asyncio, иначе не работает асинхронность и каюк !!!
    Использовать для тестовой БД, не добавяет кортежи, но может создать структуру отношений.
    Затести у себя, чтобы убедиться, что всё работает.
    """
    # Создать все таблицы (обычно для тестовой БД)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Проверить работу модели User
    async with async_session() as session:
        # Создать пользователя
        user = User(username="testuser", hashed_password="hash")
        session.add(user)
        await session.commit()
        # Прочитать пользователя
        result = await session.execute(select(User).where(User.username == "testuser"))
        user_obj = result.scalar_one()
        assert user_obj.username == "testuser"
        # Удалить пользователя
        await session.delete(user_obj)
        await session.commit()
        # Проверить, что пользователя нет
        result = await session.execute(select(User).where(User.username == "testuser"))
        assert result.scalar_one_or_none() is None

# TODO: добавить авторизацию и получение user_id из токена
from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from io import BytesIO
from app.middleware.logging import logger
from app.database.connection import Base, engine
from uuid import uuid4, UUID
from typing import Tuple
from app.models.models import UserDataItem
from app.database.connection import async_session


router = APIRouter()


@router.post("/csv")
async def upload_csv(name: str = "blank", user_id: int = -1, file: UploadFile = File(...)) -> dict:
    """
    Обрабатывает загрузку CSV файла через POST-запрос.

    Args:
        name (str): Имя графика, вписывают юзер на клиенте.
        file (UploadFile): Загружаемый CSV-файл, передается через multipart/form-data.

    Returns:
        dict: Словарь с именем файла и preview первых строк в виде списка словарей.

    Raises:
        HTTPException: Возникает при неверном типе файла или ошибке парсинга CSV.

    Логируется успешная загрузка и ошибки парсинга.
    """
    if not file.content_type.startswith("text/csv") and not file.filename.endswith(".csv"):
        logger.error(f"Попытка загрузить файл с неподдерживаемым типом: {file.content_type}")
        raise HTTPException(status_code=400, detail="Неверный тип файла")
    contents = await file.read()
    try:
        df = pd.read_csv(BytesIO(contents))
        logger.info(f"Файл {file.filename} успешно загружен и распарсен.")
    except Exception as e:
        logger.error(f"Ошибка парсинга CSV файла {file.filename}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Ошибка парсинга CSV: {str(e)}")
    data_id, df_len = await load_df_to_db(name, uuid4(), df)
    add_to_UserDataItem(user_id, data_id)
    return {"data_id": data_id, "rows": df_len, "preview": df.head().to_dict(orient="records")}


async def load_df_to_db(name: str, uuid: UUID, df: pd.DataFrame) -> Tuple[str, int]:
    """
    Загружает DataFrame в БД в новую таблицу и возвращает (имя_таблицы, число_строк).

    Args: df (pd.DataFrame): DataFrame для загрузки.
        name (str): Базовое имя для таблицы.
        uuid (UUID): Уникальный идентификатор для таблицы.
    Returns:
        Tuple[str, int]: Кортеж с именем созданной таблицы и числом строк.
    Raises:
        ValueError: При ошибке загрузки данных в таблицу.
    """
    data_id = f"{name}_{uuid.hex}"
    async with engine.begin() as conn:
        # при необходимости создаст отсутствующие таблицы из метаданных
        await conn.run_sync(Base.metadata.create_all)
        # вызов синхронного pandas.to_sql на синхронном соединении внутри run_sync
        try:
            await conn.run_sync(
                lambda sync_conn: df.to_sql(
                    name=data_id,
                    con=sync_conn,
                    if_exists="fail",
                    index=False,
                    method="multi",
                )
            )
        except ValueError as ve:
            logger.error(f"Ошибка при загрузке DataFrame в таблицу {data_id}: {str(ve)}")
            raise HTTPException(status_code=400, detail=f"Ошибка при загрузке данных: {str(ve)}")
        logger.info(f"DataFrame успешно загружен в таблицу {data_id} с {len(df)} строками.")
    return data_id, len(df)


async def add_to_UserDataItem(user_id: int, data_id: str):
    """
    Добавляет запись о загруженных данных пользователя в таблицу UserDataItem.

    Args:
        user_id (int): ID пользователя.
        data_id (str): Имя таблицы с загруженными данными.

    Raises:
        HTTPException: При ошибке добавления записи в базу данных.
    """
    async with async_session() as session:
        try:
            user_data_item = UserDataItem(user_id=user_id, data_id=data_id)
            session.add(user_data_item)
            await session.commit()
            logger.info(f"Запись о данных пользователя {user_id} для таблицы {data_id} успешно добавлена.")
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка при добавлении записи о данных пользователя {user_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Ошибка при сохранении данных пользователя")

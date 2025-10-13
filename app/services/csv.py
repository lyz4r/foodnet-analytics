from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from io import BytesIO
from app.middleware.logging import logger
from app.database.connection import Base, engine
from uuid import uuid4, UUID
from typing import Tuple


router = APIRouter()


@router.post("/csv")
async def upload_csv(name: str = "blank", file: UploadFile = File(...)) -> dict:
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
    table_name, df_len = await load_df_to_db(name, uuid4(), df)
    return {"table_name": table_name, "rows": df_len, "preview": df.head().to_dict(orient="records")}


async def load_df_to_db(name: str, uuid: UUID, df: pd.DataFrame) -> Tuple[str, int]:
    """
    Загружает DataFrame в БД в новую таблицу и возвращает (имя_таблицы, число_строк).
    """
    table_name = f"{name}_{uuid.hex}"
    async with engine.begin() as conn:
        # при необходимости создаст отсутствующие таблицы из метаданных
        await conn.run_sync(Base.metadata.create_all)
        # вызов синхронного pandas.to_sql на синхронном соединении внутри run_sync
        try:
            await conn.run_sync(
                lambda sync_conn: df.to_sql(
                    name=table_name,
                    con=sync_conn,
                    if_exists="fail",
                    index=False,
                    method="multi",
                )
            )
        except ValueError as ve:
            logger.error(f"Ошибка при загрузке DataFrame в таблицу {table_name}: {str(ve)}")
            raise HTTPException(status_code=400, detail=f"Ошибка при загрузке данных: {str(ve)}")
        logger.info(f"DataFrame успешно загружен в таблицу {table_name} с {len(df)} строками.")
    return table_name, len(df)

from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from io import BytesIO
from app.middleware.logging import logger

router = APIRouter()


@router.post("/csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Обрабатывает загрузку CSV файла через POST-запрос.

    Args:
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
    preview = df.head().to_dict(orient="records")
    return {"filename": file.filename, "preview": preview}

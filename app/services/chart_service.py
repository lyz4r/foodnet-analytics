from fastapi import APIRouter, Body, HTTPException, status
from typing import List, Dict, Optional, Any
import altair as alt
import pandas as pd
from app.middleware.logging import logger
from app.models.schemas import ChartData


router = APIRouter()


class ChartGenerator:
    """Класс для генерации графиков на основе типа"""

    SUPPORTED_CHARTS = {
        "line": lambda df, enc: alt.Chart(df).mark_line().encode(**enc),
        "bar": lambda df, enc: alt.Chart(df).mark_bar().encode(**enc),
        "scatter": lambda df, enc: alt.Chart(df).mark_point().encode(**enc),
    }

    @staticmethod
    def create_pie_chart(df: pd.DataFrame, y_field: str, x_field: str) -> alt.Chart:
        """Специальный метод для pie chart с другой логикой encoding"""
        return alt.Chart(df).mark_arc().encode(
            theta=alt.Theta(f"{y_field}:Q"),
            color=alt.Color(f"{x_field}:N")
        )

    @classmethod
    def generate(cls, chart_type: str, df: pd.DataFrame, encoding: Dict[str, alt.X | alt.Y | alt.Color],
                 x_field: str, y_field: str) -> alt.Chart:
        """Генерирует график нужного типа"""
        if chart_type == "pie":
            chart = cls.create_pie_chart(df, y_field, x_field)
        else:
            chart_func = cls.SUPPORTED_CHARTS.get(chart_type)
            chart = chart_func(df, encoding)

        return chart.properties(title="FoodNet Analytics Chart")


def validate_dataframe_fields(df: pd.DataFrame, x_field: str, y_field: str, color_field: Optional[str] = None) -> None:
    """Проверяет наличие необходимых полей в DataFrame"""
    required_fields = [x_field, y_field]
    if color_field:
        required_fields.append(color_field)
    missing_fields = [field for field in required_fields if field not in df.columns]
    if missing_fields:
        raise ValueError(f"Отсутствуют обязательные поля в данных: {missing_fields}")


def prepare_dataframe(data: List[Dict[str, Any]], x_field: str) -> pd.DataFrame:
    """Преобразует данные в DataFrame и обрабатывает типы"""
    df = pd.DataFrame(data)

    try:
        df[x_field] = pd.to_datetime(df[x_field])
    except Exception as e:
        logger.warning(f"Не удалось преобразовать поле {x_field} в datetime: {e}. Используется исходный тип.")

    return df


def build_encoding(x_field: str, y_field: str, color_field: Optional[str] = None) -> Dict[str, alt.X | alt.Y | alt.Color]:
    """Строит encoding для графика"""
    encoding = {
        "x": alt.X(f"{x_field}:T", title=x_field.capitalize()),
        "y": alt.Y(f"{y_field}:Q", title=y_field.capitalize())
    }

    if color_field:
        encoding["color"] = alt.Color(f"{color_field}:N", title=color_field.capitalize())

    return encoding


def prepare_chart_response(chart: alt.Chart, df: pd.DataFrame) -> Dict[str, Any]:
    """Подготавливает финальный ответ с графиком"""
    chart_dict = chart.to_dict()
    chart_dict["data"] = {"values": df.to_dict(orient="records")}

    # Удаляем datasets если существует
    chart_dict.pop("datasets", None)

    return chart_dict


@router.post("/generate_chart", status_code=status.HTTP_200_OK)
async def generate_chart(chart_data: ChartData = Body(...)) -> Dict[str, Any]:
    """
    Генерирует график на основе переданных данных


    Args:
        chart_data: Данные для построения графика


    Returns:
        Dict с конфигурацией Altair графика


    Raises:
        HTTPException: При ошибках валидации или генерации графика
    """
    try:
        logger.info(f"Генерация графика типа {chart_data.chart_type} для полей: x={chart_data.x_field}, y={chart_data.y_field}")

        # Подготовка данных
        df = prepare_dataframe(chart_data.data, chart_data.x_field)

        # Валидация наличия полей
        validate_dataframe_fields(df, chart_data.x_field, chart_data.y_field, chart_data.color_field)

        # Построение encoding
        encoding = build_encoding(chart_data.x_field, chart_data.y_field, chart_data.color_field)

        # Генерация графика
        chart = ChartGenerator.generate(
            chart_data.chart_type,
            df,
            encoding,
            chart_data.x_field,
            chart_data.y_field
        )

        # Подготовка ответа
        chart_dict = prepare_chart_response(chart, df)

        logger.info(f"График типа {chart_data.chart_type} успешно сгенерирован")
        return chart_dict

    except ValueError as e:
        logger.error(f"Ошибка валидации: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации: {str(e)}"
        )
    except KeyError as e:
        logger.error(f"Отсутствует обязательное поле в данных: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Отсутствует обязательное поле: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при генерации графика: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при генерации графика"
        )

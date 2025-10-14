# TODO: исправить всё плохое
# что плохо: 1) все содержание функции в защищенном блоке try-except, 2) нет логирования ошибок, 3) нет проверки входных данных (типизации),
# 4)бесконечные if else, сделай это изящнее, 5) нет проверки на наличие необходимых полей в данных
from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Optional
import altair as alt
import pandas as pd

app = FastAPI(title="FoodNet Analytics Graph Service")


class ChartData(BaseModel):
    data: List[Dict[str, str | float]]  # Строки для date, числа для calories
    chart_type: str
    x_field: str
    y_field: str
    color_field: Optional[str] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)


@app.post("/generate_chart")
async def generate_chart(chart_data: ChartData = Body(...)):
    try:
        # Преобразуем данные в Pandas DataFrame
        df = pd.DataFrame(chart_data.data)
        # Убеждаемся, что date интерпретируется как дата
        df[chart_data.x_field] = pd.to_datetime(df[chart_data.x_field])

        encoding = {
            "x": alt.X(chart_data.x_field + ":T", title=chart_data.x_field.capitalize()),  # Явно указываем тип
            "y": alt.Y(chart_data.y_field + ":Q", title=chart_data.y_field.capitalize())
        }
        if chart_data.color_field:
            encoding["color"] = alt.Color(chart_data.color_field + ":N", title=chart_data.color_field.capitalize())

        if chart_data.chart_type == "line":
            chart = alt.Chart(df).mark_line().encode(**encoding).properties(title="FoodNet Analytics Chart")
        elif chart_data.chart_type == "bar":
            chart = alt.Chart(df).mark_bar().encode(**encoding).properties(title="FoodNet Analytics Chart")
        elif chart_data.chart_type == "scatter":
            chart = alt.Chart(df).mark_point().encode(**encoding).properties(title="FoodNet Analytics Chart")
        elif chart_data.chart_type == "pie":
            chart = alt.Chart(df).mark_arc().encode(
                theta=alt.Theta(chart_data.y_field + ":Q"),
                color=alt.Color(chart_data.x_field + ":N") if chart_data.color_field else alt.Color(chart_data.x_field + ":N")
            ).properties(title="FoodNet Analytics Chart")
        else:
            raise HTTPException(status_code=400, detail="Unsupported chart type")

        chart_dict = chart.to_dict()
        chart_dict["data"] = {"values": [dict(row) for row in df.to_dict(orient="records")]}  # Явно встраиваем данные
        del chart_dict["datasets"]  # Удаляем datasets

        print("Generated chart:", chart_dict)  # Отладка
        return chart_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

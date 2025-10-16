from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_generate_chart():
    chart_request = {
        "data": [
            {"date": "2025-01-01", "calories": 2100, "category": "weekday"},
            {"date": "2025-01-02", "calories": 2300, "category": "weekday"},
            {"date": "2025-01-03", "calories": 2200, "category": "weekday"},
            {"date": "2025-01-04", "calories": 1900, "category": "weekday"},
            {"date": "2025-01-05", "calories": 2400, "category": "weekday"},
            {"date": "2025-01-06", "calories": 2800, "category": "weekend"},
            {"date": "2025-01-07", "calories": 2600, "category": "weekend"}
        ],
        "chart_type": "line",
        "x_field": "date",
        "y_field": "calories",
        "color_field": "category"
    }
    response = client.post("/chart/generate_chart", json=chart_request)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data

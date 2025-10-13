from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_upload_csv():
    csv_content = "col1,col2\n1,2\n3,4\n"
    files = {"file": ("test.csv", csv_content, "text/csv")}
    response = client.post("/upload/csv", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["rows"] == 2
    assert "table_name" in data

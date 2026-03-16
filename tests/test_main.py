import io
import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).parent.parent / "src"))
from main import app

PASSWORD = "c2FzaGFiZXN0MQ=="
CLEAN_PASSWORD = "sashabest1"

@pytest.fixture
def client():
    """Создаёт тестовый клиент"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture()
def mock_sup_func():
    """Мок для функции sup_func.smart_open"""
    with patch("main.sup_func.smart_open") as mock:
        yield mock

def test_open_file_no_file(client):
    """Тест отсутствует файл в запросе"""
    response = client.post("/open_file", data = {})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["message"] == "Нет файла в запросе"
    assert data["success"] == False

def test_open_file_empty_filename(client):
    """Тест пустое имя файла"""
    data = {
        "file": (io.BytesIO(b"best content"), ""),
        "password": PASSWORD
    }
    response = client.post("/open_file", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] == False
    assert data["message"] == "Имя файла пустое"

def test_open_file_no_pass(client):
    data = {
        "file": (io.BytesIO(b"best_content"),"test.txt"),
        "password": ""
    }
    response = client.post("/open_file", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["message"] == "Поле для пароля пустое"
    assert data["success"] == False

def test_sup_func_called_correctly(client, mock_sup_func):
    test_content = b"test file content"
    mock_sup_func.return_value = {"success": True, "code": 200, "message": "Файл загружен"}
    data = {
        "file": (io.BytesIO(test_content), "test.txt"),
        "password": PASSWORD
    }
    client.post("/open_file",data=data, content_type="multipart/form-data")
    mock_sup_func.assert_called_once()

    args, kwargs = mock_sup_func.call_args
    called_file, called_password = args

    assert CLEAN_PASSWORD == called_password
    assert called_file.filename == "test.txt"
    assert hasattr(called_file, "save")


import io
import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).parent.parent / "src"))
from main import app

PASSWORD = "c2FzaGFiZXN0MQ=="
INCORRECT_PASSWORD = "SGVsbG8sIGkgbGlrZSBzdHJvbmcgbWFu"
PASSWORD_NO_BASE64 = "c2FzaGFiZXN0MQ"

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
    assert data["code"] == 18

def test_open_file_empty_filename(client):
    """Тест пустое имя файла"""
    data = {
        "file": (io.BytesIO(b"best content"), ""),
        "password": PASSWORD
    }
    response = client.post("/open_file", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["code"] == 17

def test_open_file_no_pass(client):
    data = {
        "file": (io.BytesIO(b"best_content"),"test.txt"),
        "password": ""
    }
    response = client.post("/open_file", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["code"] == 19

def test_sup_func_called_correctly(client, mock_sup_func):
    test_content = b"test file content"
    mock_sup_func.return_value = 0
    data = {
        "file": (io.BytesIO(test_content), "test.txt"),
        "password": PASSWORD
    }
    client.post("/open_file",data=data, content_type="multipart/form-data")
    mock_sup_func.assert_called_once()

    args, kwargs = mock_sup_func.call_args
    called_file, called_password = args

    assert PASSWORD == called_password
    assert called_file.filename == "test.txt"
    assert hasattr(called_file, "save")
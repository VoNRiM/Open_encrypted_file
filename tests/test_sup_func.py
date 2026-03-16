import io
import sys
from pathlib import Path
from werkzeug.datastructures import FileStorage

PASSWORD = "sashabest1"
INCORRECT_PASSWORD = "sashanobest1"
TEST_DATA_DIR = Path(__file__).parent / "test_data"

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from sup_func import (
    check_filetype,
    smart_open,
)

def create_flask_file(file_path:Path)-> FileStorage:
    """Создаёт файл FileStorage на основе обычного файла, для проведения тестов
    :param: file_path: Путь к файлу, который мы пересоздать для тестов.
    :return: FileStorage: файл объект похожий на тот который передаёт Flask
    """
    with open(file_path, "rb") as f:
        content = f.read()
    return FileStorage(
        stream=io.BytesIO(content),
        filename=Path(file_path).name,
        name="file",
        content_type="application/octet-stream"
    )

def test_tar_smart_open():
    """Проверка файла неизвестного формата"""
    file_path = TEST_DATA_DIR / "test_tar.tar.xz"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400

def test_zip_smart_open():
    """Проверка файла zip формата """
    file_path = TEST_DATA_DIR / "test_zip.zip"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == True
    assert result["code"] == 200
    assert result["message"] == "Файл загружен"

def test_rar_smart_open():
    """Проверка файла rar формата """
    file_path = TEST_DATA_DIR / "test_rar.rar"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == True
    assert result["code"] == 200
    assert result["message"] == "Файл загружен"

def test_7z_smart_open():
    """Проверка файла 7z формата """
    file_path = TEST_DATA_DIR / "test_7z.7z"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == True
    assert result["code"] == 200
    assert result["message"] == "Файл загружен"

def test_word_doc_smart_open():
    """Проверка файла doc формата """
    file_path = TEST_DATA_DIR / "test_word.DOCX"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == True
    assert result["code"] == 200
    assert result["message"] == "Файл загружен"

def test_excel_smart_open():
    """Проверка файла excel формата """
    file_path = TEST_DATA_DIR / "test_excel.xlsx"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == True
    assert result["code"] == 200
    assert result["message"] == "Файл загружен"

def test_powerpoint_smart_open():
    """Проверка файла pptx формата """
    file_path = TEST_DATA_DIR / "test_powerpoint.pptx"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == True
    assert result["code"] == 200
    assert result["message"] == "Файл загружен"

def test_pdf_smart_open():
    """Проверка файла pdf формата """
    file_path = TEST_DATA_DIR / "test_pdf.pdf"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == True
    assert result["code"] == 200
    assert result["message"] == "Файл загружен"


def test_zip_smart_open_incorrect_pas():
    """Проверка файла zip формата c неправильным паролем"""
    file_path = TEST_DATA_DIR / "test_zip.zip"
    file = create_flask_file(file_path)
    result = smart_open(file, INCORRECT_PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400
    assert result["message"] == "Неверный пароль"

def test_rar_smart_open_incorrect_pas():
    """Проверка файла rar формата c неправильным паролем"""
    file_path = TEST_DATA_DIR / "test_rar.rar"
    file = create_flask_file(file_path)
    result = smart_open(file, INCORRECT_PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400
    assert result["message"] == "Неверный пароль"

def test_7z_smart_open_incorrect_pas():
    """Проверка файла 7z формата с неправильным паролем"""
    file_path = TEST_DATA_DIR / "test_7z.7z"
    file = create_flask_file(file_path)
    result = smart_open(file, INCORRECT_PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400
    assert result["message"] == "Неверный пароль"

def test_word_doc_smart_open_incorrect_pas():
    """Проверка файла doc формата c неправильным паролем"""
    file_path = TEST_DATA_DIR / "test_word.DOCX"
    file = create_flask_file(file_path)
    result = smart_open(file, INCORRECT_PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400
    assert result["message"] == "Неверный пароль"

def test_excel_smart_open_incorrect_pas():
    """Проверка файла excel формата c неправильным паролем"""
    file_path = TEST_DATA_DIR / "test_excel.xlsx"
    file = create_flask_file(file_path)
    result = smart_open(file, INCORRECT_PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400
    assert result["message"] == "Неверный пароль"

def test_powerpoint_smart_open_incorrect_pas():
    """Проверка файла pptx формата c неправильным паролем"""
    file_path = TEST_DATA_DIR / "test_powerpoint.pptx"
    file = create_flask_file(file_path)
    result = smart_open(file, INCORRECT_PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400
    assert result["message"] == "Неверный пароль"

def test_pdf_smart_open_incorrect_pas():
    """Проверка файла pdf формата c неправильным паролем"""
    file_path = TEST_DATA_DIR / "test_pdf.pdf"
    file = create_flask_file(file_path)
    result = smart_open(file, INCORRECT_PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400
    assert result["message"] == "Неверный пароль"


def test_check_file_type_tar():
    """Проверка функций определения типа файла которого нет в списке"""
    file = TEST_DATA_DIR / "test_tar.tar.xz"
    result = check_filetype(str(file))
    assert result == False

def test_check_file_type_zip():
    """Проверка функций определения типа файла"""
    file = TEST_DATA_DIR / "test_rar.rar"
    result = check_filetype(str(file))
    assert result == "rar"

def test_check_file_type_7z():
    """Проверка функций определения типа файла"""
    file = TEST_DATA_DIR / "test_7z.7z"
    result = check_filetype(str(file))
    assert result == "7z"


def test_check_file_type_pdf():
    """Проверка функций определения типа файла"""
    file = TEST_DATA_DIR / "test_pdf.pdf"
    result = check_filetype(str(file))
    assert result == "pdf"

def test_check_file_type_docx():
    """Проверка функций определения типа файла"""
    file = TEST_DATA_DIR / "test_word.DOCX"
    result = check_filetype(str(file))
    assert result == "ole"

def test_check_file_type_excel():
    """Проверка функций определения типа файла"""
    file = TEST_DATA_DIR / "test_excel.xlsx"
    result = check_filetype(str(file))
    assert result == "ole"

def test_check_file_type_pptx():
    """Проверка функций определения типа файла"""
    file = TEST_DATA_DIR / "test_powerpoint.pptx"
    result = check_filetype(str(file))
    assert result == "ole"

def test_pdf_no_password():
    """Проверка на PDF файл без пароля"""
    file_path = TEST_DATA_DIR / "test_pdf_no_pass.pdf"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400
    assert result["message"] == "Файл не зашифрован"

def test_zip_no_password():
    """Проверка на zip файл без пароля"""
    file_path = TEST_DATA_DIR / "test_zip_no_pass.zip"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400
    assert result["message"] == "Файл не зашифрован"

def test_7z_no_password():
    """Проверка на 7z файл без пароля"""
    file_path = TEST_DATA_DIR / "test_7z_no_pass.7z"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400
    assert result["message"] == "Файл не зашифрован"

def test_rar_no_password():
    """Проверка на rar файл без пароля"""
    file_path = TEST_DATA_DIR / "test_rar_no_pass.rar"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400
    assert result["message"] == "Файл не зашифрован"

def test_docx_no_password():
    """Проверка на word файл без пароля"""
    file_path = TEST_DATA_DIR / "test_word_no_pass.DOCX"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400
    assert result["message"] == "Файл не зашифрован"

def test_ppoint_no_password():
    """Проверка на powepoint файл без пароля"""
    file_path = TEST_DATA_DIR / "test_powerpoint_no_pass.pptx"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400
    assert result["message"] == "Файл не зашифрован"

def test_excel_no_password():
    """Проверка на excel файл без пароля"""
    file_path = TEST_DATA_DIR / "test_excel_no_pass.xlsx"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400
    assert result["message"] == "Файл не зашифрован"

def test_file_empty():
    """Проверка пустого файла"""
    file_path = TEST_DATA_DIR / "test_word_empty.DOCX"
    file = create_flask_file(file_path)
    result = smart_open(file, PASSWORD)
    assert result["success"] == False
    assert result["code"] == 400
    assert result["message"] == "Файл пуст"

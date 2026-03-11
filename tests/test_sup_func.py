import sys
from pathlib import Path
import shutil
PASSWORD = "c2FzaGFiZXN0MQ=="
INCORRECT_PASSWORD = "SGVsbG8sIGkgbGlrZSBzdHJvbmcgbWFu"
PASSWORD_NO_BASE64 = "c2FzaGFiZXN0MQ"
TEST_DATA_DIR = Path(__file__).parent / "test_data"


sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from sup_func import (
    check_filetype,
    smart_open,
)
class FlaskFile:
    def __init__(self, path):
        self.path = path
        self.filename = path.name

    def save(self, dst_path):
        shutil.copy2(self.path, dst_path)

def test_tar_smart_open():
    """Проверка файла неизвестного формата"""
    file = TEST_DATA_DIR / "test_tar.tar.xz"
    result = smart_open(FlaskFile(file), PASSWORD)
    assert result == 12

def test_zip_smart_open():
    """Проверка файла zip формата """
    file = TEST_DATA_DIR / "test_zip.zip"
    result = smart_open(FlaskFile(file), PASSWORD)
    assert result == 0

def test_rar_smart_open():
    """Проверка файла rar формата """
    file = TEST_DATA_DIR / "test_rar.rar"
    result = smart_open(FlaskFile(file), PASSWORD)
    assert result == 0

def test_7z_smart_open():
    """Проверка файла 7z формата """
    file = TEST_DATA_DIR / "test_7z.7z"
    result = smart_open(FlaskFile(file), PASSWORD)
    assert result == 0

def test_word_doc_smart_open():
    """Проверка файла doc формата """
    file = TEST_DATA_DIR / "test_word.DOCX"
    result = smart_open(FlaskFile(file), PASSWORD)
    assert result == 0

def test_excel_smart_open():
    """Проверка файла excel формата """
    file = TEST_DATA_DIR / "test_excel.xlsx"
    result = smart_open(FlaskFile(file), PASSWORD)
    assert result == 0

def test_powerpoint_smart_open():
    """Проверка файла pptx формата """
    file = TEST_DATA_DIR / "test_powerpoint.pptx"
    result = smart_open(FlaskFile(file), PASSWORD)
    assert result == 0

def test_pdf_smart_open():
    """Проверка файла pdf формата """
    file = TEST_DATA_DIR / "test_pdf.pdf"
    result = smart_open(FlaskFile(file), PASSWORD)
    assert result == 0


def test_zip_smart_open_incorrect_pas():
    """Проверка файла zip формата c неправильным паролем"""
    file = TEST_DATA_DIR / "test_zip.zip"
    result = smart_open(FlaskFile(file), INCORRECT_PASSWORD)
    assert result == 10

def test_rar_smart_open_incorrect_pas():
    """Проверка файла rar формата c неправильным паролем"""
    file = TEST_DATA_DIR / "test_rar.rar"
    result = smart_open(FlaskFile(file), INCORRECT_PASSWORD)
    assert result == 10

def test_7z_smart_open_incorrect_pas():
    """Проверка файла 7z формата c неправильным паролем"""
    file = TEST_DATA_DIR / "test_7z.7z"
    result = smart_open(FlaskFile(file), INCORRECT_PASSWORD)
    assert result == 10

def test_word_doc_smart_open_incorrect_pas():
    """Проверка файла doc формата c неправильным паролем"""
    file = TEST_DATA_DIR / "test_word.DOCX"
    result = smart_open(FlaskFile(file), INCORRECT_PASSWORD)
    assert result == 10

def test_excel_smart_open_incorrect_pas():
    """Проверка файла excel формата c неправильным паролем"""
    file = TEST_DATA_DIR / "test_excel.xlsx"
    result = smart_open(FlaskFile(file), INCORRECT_PASSWORD)
    assert result == 10

def test_powerpoint_smart_open_incorrect_pas():
    """Проверка файла pptx формата c неправильным паролем"""
    file = TEST_DATA_DIR / "test_powerpoint.pptx"
    result = smart_open(FlaskFile(file), INCORRECT_PASSWORD)
    assert result == 10

def test_pdf_smart_open_incorrect_pas():
    """Проверка файла pdf формата c неправильным паролем"""
    file = TEST_DATA_DIR / "test_pdf.pdf"
    result = smart_open(FlaskFile(file), INCORRECT_PASSWORD)
    assert result == 10

def test_smart_open_no_base_pas():
    """Проверка функции с не форматным паролем"""
    file = TEST_DATA_DIR / "test_pdf.pdf"
    result = smart_open(FlaskFile(file), PASSWORD_NO_BASE64)
    assert result == 15

def test_check_file_type_tar():
    """Проверка функций определения типа файла которого нет в списке"""
    file = TEST_DATA_DIR / "test_tar.tar.xz"
    result = check_filetype(file)
    assert result == 12

def test_check_file_type_zip():
    """Проверка функций определения типа файла"""
    file = TEST_DATA_DIR / "test_rar.rar"
    result = check_filetype(file)
    assert result == "rar"

def test_check_file_type_7z():
    """Проверка функций определения типа файла"""
    file = TEST_DATA_DIR / "test_7z.7z"
    result = check_filetype(file)
    assert result == "7z"


def test_check_file_type_pdf():
    """Проверка функций определения типа файла"""
    file = TEST_DATA_DIR / "test_pdf.pdf"
    result = check_filetype(file)
    assert result == "pdf"

def test_check_file_type_DOCX():
    """Проверка функций определения типа файла"""
    file = TEST_DATA_DIR / "test_word.DOCX"
    result = check_filetype(file)
    assert result == "ole"

def test_check_file_type_excel():
    """Проверка функций определения типа файла"""
    file = TEST_DATA_DIR / "test_excel.xlsx"
    result = check_filetype(file)
    assert result == "ole"

def test_check_file_type_pptx():
    """Проверка функций определения типа файла"""
    file = TEST_DATA_DIR / "test_powerpoint.pptx"
    result = check_filetype(file)
    assert result == "ole"

def test_pdf_no_password():
    """Проверка на PDF файл без пароля"""
    file = TEST_DATA_DIR / "test_pdf_no_pass.pdf"
    result = smart_open(FlaskFile(file), PASSWORD)
    assert result == 16

def test_zip_no_password():
    """Проверка на PDF файл без пароля"""
    file = TEST_DATA_DIR / "test_zip_no_pass.zip"
    result = smart_open(FlaskFile(file), PASSWORD)
    assert result  == 16

def test_7z_no_password():
    """Проверка на PDF файл без пароля"""
    file = TEST_DATA_DIR / "test_7z_no_pass.7z"
    result = smart_open(FlaskFile(file), PASSWORD)
    assert result  == 16

def test_rar_no_password():
    """Проверка на PDF файл без пароля"""
    file = TEST_DATA_DIR / "test_rar_no_pass.rar"
    result = smart_open(FlaskFile(file), PASSWORD)
    assert result  == 16

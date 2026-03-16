# Включённые
import tempfile
import os
import subprocess
import shutil

# Сторонние
import base64
import magic
from patoolib.util import PatoolError
from pypdf import PdfReader, PdfWriter  # PDF
from pypdf.errors import PdfReadError
import msoffcrypto  # word
import patoolib
from loguru import logger
from zipfile import ZipFile
from rarfile import RarFile
import py7zr
from werkzeug.datastructures import FileStorage

TEMP_DIR = "../temp"

password_protected_files = {
    # Архивы
    'archives': ["zip", "rar", "7z"],
    # Документы
    'documents': ["docx", "xlsx", "pptx", "doc", "xls", "ole"],
}


def check_filetype(file_path: str) -> str | bool:
    """Возвращает тип файла, определяемого по mime_map
    :param file_path: Путь, где находится файл у которого определяем тип
    :returns: str | bool
    -str: Тип файла в строке
    -False: Когда не смогли определить тип файла
    """
    mime_map = {
        # Документы
        'application/encrypted': 'ole',
        'application/x-encrypted': 'ole',
        'application/msword': 'doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'application/vnd.ms-excel': 'xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
        'application/vnd.ms-powerpoint': 'ppt',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
        'application/vnd.ms-office': 'ole',  # общий Office тип

        # Другие архивы
        "application/zip": "zip",
        'application/x-rar': 'rar',
        'application/x-7z-compressed': '7z',
        'application/x-tar': 'tar',

        # PDF
        'application/pdf': 'pdf',
    }
    file_type = magic.from_file(file_path, mime=True)
    if file_type in mime_map:
        return mime_map[file_type]
    return False


def check_archive_encrypted(temp_path: str, type_file: str) -> bool:
    """
    Проверяет действительно ли архив, который передаётся в эту функцию имеют пароль
    :param temp_path: Путь к временному файлу в виде строки
    :param type_file: Тип файла в виде строки
    :return: True | False
        True - Архив зашифрован |
        False - Архив не зашифрован
    """
    if type_file == "zip":
        with ZipFile(temp_path, "r") as Zip:
            is_encrypted = any(info.flag_bits & 0x1 for info in Zip.infolist())
    if type_file == "7z":
        with py7zr.SevenZipFile(temp_path, "r") as z:
            is_encrypted = z.needs_password()
    if type_file == "rar":
        with RarFile(temp_path, "r") as rar:
            is_encrypted = rar.needs_password()
    return is_encrypted


def open_archive_file(temp_path: str, password: str, original_name: str, type_file: str) -> dict[str, bool | int | str]:
    """
    Открывает зашифрованный архив, и сохраняет все файлы в папке temp
    :param temp_path: Путь временного файла
    :param password: Пароль от файла
    :param original_name: Имя файла для наименования папки в которой содержаться файлы
    :param type_file: Тип файла
    :return: dict[str, bool | int | str]:
        str: Ключ словаря |
        bool: Разрешён доступ или нет |
        int: Статус код |
        str: Комментарий
    """
    extract_path = os.path.join(TEMP_DIR, f"{original_name}_extracted")
    logger.info(f"Начинаем работу с {type_file}-архивом")
    is_encrypted = check_archive_encrypted(temp_path, type_file)
    if not is_encrypted:
        logger.error("Файл не зашифрован")
        return {"success": False, "code": 400, "message": "Файл не зашифрован"}
    try:
        os.makedirs(extract_path, exist_ok=True)  # Создание папки
        patoolib.extract_archive(temp_path, outdir=extract_path, password=password)
        logger.success("Распаковка завершена")
        return {"success": True, "code": 200, "message": "Файл загружен"}
    except PatoolError as e:
        # Запуск тестовой команды, чтобы увидеть детали
        if type_file == "rar":
            cmd = ['unrar', 't', f'-p{password}', temp_path]
            password_indicator = 'incorrect password'
        else:  # для 7z и zip
            cmd = ['7z', 't', f'-p{password}', temp_path]
            password_indicator = 'wrong password'
        result = subprocess.run(cmd, capture_output=True, text=True)
        stderr = result.stderr.lower()
        # Ошибка пароля
        if password_indicator in stderr:
            logger.error(f"Неверный пароль для {type_file}")
            shutil.rmtree(extract_path)
            return {"success": False, "code": 400, "message": "Неверный пароль"}
        else:
            logger.error(f"Ошибка {type_file.upper()}: {e}")
            return {"success": False, "code": 400, "message": "Ошибка чтения архива"}
    except Exception as e:
        logger.error(f"Неожиданная ошибка {e}")
        return {"success": False, "code": 400, "message": f"Неожиданная ошибка{e}"}


def open_pdf_file(temp_path: str, password: str, original_name: str) -> dict[str, bool | int | str]:
    """
    Открывает зашифрованный pdf файл и сохраняет его в папке temp
    :param temp_path: Путь временного файла
    :param password: Пароль от файла
    :param original_name: Имя файла
    :return: dict[str, bool | int | str]:
        str: Ключ словаря |
        bool: Разрешён доступ или нет |
        int: Статус код |
        str: Комментарий
    """
    reader = PdfReader(temp_path)
    output_path = os.path.join(TEMP_DIR, f"decrypted_{os.path.basename(original_name)}")
    if not reader.is_encrypted:
        logger.error("Файл не зашифрован")
        return {"success": False, "code": 400, "message": "Файл не зашифрован"}
    try:
        result = reader.decrypt(password)
        logger.debug("Мы прочитали файл")
        if result == 1:
            writer = PdfWriter()
            for page in reader.pages:  # Копируем по странице
                writer.add_page(page)
            logger.info(f"Cохраняем файл по адресу {output_path}")
            with open(output_path, "wb") as f:
                writer.write(f)
            logger.success("Запись файла прошла успешно")
            return {"success": True, "code": 200, "message": "Файл загружен"}
        else:
            logger.error("Неверный пароль")
            return {"success": False, "code": 400, "message": "Неверный пароль"}
    except PdfReadError as e:  # Ошибка чтения PDF
        logger.error(f"Ошибка PDF: {e}")
        return {"success": False, "code": 400, "message": "Ошибка чтения файла"}
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        return {"success": False, "code": 500, "message": f"Неизвестная ошибка: {e}"}


def open_word_file(temp_path: str, password: str, original_name: str) -> dict[str, bool | int | str]:
    """
    Открывает зашифрованный word файл и сохраняет его в папке temp
    :param temp_path: Путь временного файла
    :param password: Пароль от файла
    :param original_name: Имя файла
    :return: dict[str, bool | int | str]:
        str: Ключ словаря |
        bool: Разрешён доступ или нет |
        int: Статус код |
        str: Комментарий
    """
    with open(temp_path, "rb") as f:
        office_file = msoffcrypto.OfficeFile(f)
        if not office_file.is_encrypted():
            logger.error("Файл не зашифрован")
            return {"success": False, "code": 400, "message": "Файл не зашифрован"}
        try:
            office_file.load_key(password=password)
            output_path = os.path.join(TEMP_DIR, f"decrypted_{os.path.basename(original_name)}")
            with open(output_path, 'wb') as of:
                office_file.decrypt(of)
            return {"success": True, "code": 200, "message": "Файл загружен"}

        except Exception as e:
            print(str(e))
            if "password" in str(e):
                logger.error("Неверный пароль")
                return {"success": False, "code": 400, "message": "Неверный пароль"}
            else:
                return {"success": False, "code": 500, "message": f"Неизвестная ошибка: {e}"}


def smart_open(file: FileStorage, password: str) -> dict[str, bool | int | str]:
    """
    Функция распределяющая, какая функция требуется  для открытия
    конкретного типа файла
    :param file: Объект загруженного файла
    :param password: Пароль от файла
    :returns: dict[str, bool | int | str]:
        str: Ключ словаря |
        bool: Разрешён доступ или нет |
        int: Статус код |
        str: Комментарий
    """
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file.save(tmp.name)
        temp_path = tmp.name
        original_name = file.filename
    try:
        file_size = os.path.getsize(temp_path)
        if file_size == 0:
            logger.error("Файл пуст")
            return {"success": False, "code": 400, "message": "Файл пуст"}
        file_type = check_filetype(temp_path)
        if not file_type:
            logger.error("Неизвестный тип файла")
            return {"success": False, "code": 400, "message": "Неизвестный тип файла"}
        else:
            logger.info(f"Тип файла: {file_type}")
            if file_type in password_protected_files["archives"]:
                result = open_archive_file(temp_path, password, original_name, file_type)
                return result
            elif file_type in password_protected_files["documents"]:
                result = open_word_file(temp_path, password, original_name)
                return result
            elif file_type == "pdf":
                result = open_pdf_file(temp_path, password, original_name)
                return result
            else:
                logger.error("Неподдерживаемый тип файла")
            return {"success": False, "code": 400, "message": "Неподдерживаемый тип файла"}
    except Exception as e:
        return {"success": False, "code": 500, "message": f"Неизвестная ошибка: {e}"}
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            logger.debug(f"Временный файл удалён")


def is_base64(password: str) -> bool:
    """Проверка является ли пароль формату base64
    :param password: Пароль в виде строки
    :returns: True - Пароль в формате base 64 |
        False - Пароль не в формате base 64
    """
    try:
        return base64.b64encode(base64.b64decode(password)) == password
    except Exception:
        return False

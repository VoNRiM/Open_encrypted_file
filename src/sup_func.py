#Включённые
import tempfile
import os
import subprocess
import shutil

# Сторонние
import base64
import magic
from patoolib.util import PatoolError
from pypdf import PdfReader, PdfWriter #PDF
from pypdf.errors import  PdfReadError
import msoffcrypto #word
import patoolib
from loguru import logger
from zipfile import ZipFile
from rarfile import RarFile
import py7zr

# Пароль от файлов: c2FzaGFiZXN0MQ==

logger.add("debug.log",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
           level="DEBUG",
           rotation="10 MB",
           retention=5,
           encoding="utf-8")

password_protected_files = {
    #Архивы
    'archives': ["zip", "rar", "7z"],
    #Документы
    'documents': ["docx", "xlsx", "pptx", "doc", "xls", "ole"],

}

def check_filetype(file_path):
    """Возвращает тип файла"""
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
    if file_type == "application/zip":
        with ZipFile(file_path, "r") as z:
            files = str(z.namelist())
            if "word/" in files:
                return "docx"
            elif "xl/" in files:
                return "xlsx"
            elif "ppt/" in files:
                return "pptx"
            return "zip"
    # Потом проверяем по словарю
    if file_type in mime_map:
        return mime_map[file_type]
    return 12


def check_archive_encrypted(temp_path, type_file):
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


def open_archive_file(temp_path, password, original_name, type_file):
    """Открывает зашифрованный архив-файл"""
    clean_password = base64.b64decode(password).decode("utf-8")
    extract_path = os.path.join("../temp", f"{original_name}_extracted")
    logger.info(f"Начинаем работу с {type_file}-архивом")
    is_encrypted = check_archive_encrypted(temp_path, type_file)
    if  not is_encrypted:
        logger.error("Файл не зашифрован")
        return 16
    try:
        os.makedirs(extract_path,exist_ok=True) # Создание папки
        patoolib.extract_archive(temp_path, outdir=extract_path, password=clean_password)
        logger.success("Распаковка завершена")
        return 0
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
            return 10
        else:
            logger.error(f"Ошибка {type_file.upper()}: {e}")
            return 11
    except Exception as e:
        logger.error(f"Неожиданная ошибка {e}")
        return 12



def open_pdf_file(temp_path, password, original_name):
    """Открывает зашифрованный PDF файл"""
    clean_password = base64.b64decode(password).decode("utf-8")
    reader = PdfReader(temp_path)
    output_path =  os.path.join("../temp", f"decrypted_{os.path.basename(original_name)}")
    if not reader.is_encrypted:
        logger.error("Файл не зашифрован")
        return 16
    try:
        result = reader.decrypt(clean_password)
        logger.debug("Мы прочитали файл")
        if result == 1:
            writer = PdfWriter()
            for page in reader.pages: # Копируем по странице
                writer.add_page(page)
            logger.info(f"Cохраняем файл по адресу {output_path}")
            with open (output_path, "wb") as f:
                writer.write(f)
            logger.success("Запись файла прошла успешно")
            return 0
        else:
            logger.error("Неверный пароль")
            return 10
    except PdfReadError as e: # Ошибка чтения PDF
        logger.error(f"Ошибка PDF: {e}")
        return 11
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        return f"Неизвестная ошибка{e}"

def open_word_file(temp_path, password,original_name):
    """Открывает зашифрованный ворд-файл"""
    clean_password = base64.b64decode(password).decode("utf-8")
    with open(temp_path, "rb") as f:
        office_file = msoffcrypto.OfficeFile(f)
        if not office_file.is_encrypted():
            logger.error("Файл не зашифрован")
            return 16
        try:
            office_file.load_key(password=clean_password)
            output_path = os.path.join("../temp", f"decrypted_{os.path.basename(original_name)}")
            with open(output_path, 'wb') as of:
                office_file.decrypt(of)
            return 0
        except Exception as e:
            print(str(e))
            if "password" in str(e):
                logger.error("Неверный пароль")
                return 10
            else:
                logger.error(f"Неизвестная ошибка:{e}")


def smart_open(file, password):
    """Функция сортировки файлов"""
    if not is_base64_format(password):
        logger.error("Пароль не является формата Base64")
        return 15
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file.save(tmp.name)
        temp_path = tmp.name
        original_name = file.filename
    try:
        file_size = os.path.getsize(temp_path)
        if file_size == 0:
            logger.error("Файл пуст")
            return 21
        file_type = check_filetype(temp_path)
        if file_type == 12:
            logger.error("Неизвестный тип файла")
            return 12
        else:
            logger.info(f"Тип файла: {file_type}")
            if file_type in password_protected_files["archives"]:
                result = open_archive_file(temp_path,password,original_name,file_type)
                return result
            elif file_type in password_protected_files["documents"]:
                result = open_word_file(temp_path, password, original_name)
                return result
            elif file_type == "pdf":
                result = open_pdf_file(temp_path, password,original_name)
                return result
            return 12
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            logger.debug(f"Временный файл удалён")

def is_base64_format(password):
    """Проверка является ли пароль формату base64"""
    if len(password) % 4 == 0:
        return True
    else:
        return False
import hashlib

from sqlalchemy import Column, Integer, String, Index
from sqlalchemy.exc import IntegrityError
from db_engine import Base, engine
from sqlalchemy.orm import sessionmaker
from loguru import logger
from pathlib import Path
from typing import Any

ONE_MILLION_WRITES = 1_000_000
BATCH_SIZE = 10_000


def calculate_file_hash(file_path: Path) -> str | None:
    """Вычисляет хэш файла
    :param file_path: Путь до определяемого файла
    :returns:
        str: Хэш файла при успехе
        None: Не удалось вычислить
    """
    try:
        md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5.update(chunk)
        return md5.hexdigest()
    except Exception as e:
        logger.error(f"Ошибка вычисления кэша{e}")
        return None


class WhiteList(Base):
    """Класс в котором определяется таблица White_list"""
    __tablename__ = "white_list"
    id = Column(Integer, primary_key=True, index=True)
    hash = Column(String(64), nullable=False, unique=True, index=True)
    file_name = Column(String, nullable=False)
    __table_args__ = (
        Index("idx_white_filename_trgm", file_name,
              postgresql_using='gin', postgresql_ops={"file_name": "gin_trgm_ops"}),
        Index("idx_white_hash_trgm", hash,
              postgresql_using='gin', postgresql_ops={"hash": "gin_trgm_ops"})
    )

class BlackList(Base):
    """Класс в котором определяется таблица Black_list"""
    __tablename__ = "black_list"
    id = Column(Integer, primary_key=True, index=True)
    hash = Column(String(64), nullable=False, unique=True, index=True)
    file_name = Column(String, nullable=False)
    __table_args__ = (
        Index("idx_black_filename_trgm", file_name,
              postgresql_using='gin', postgresql_ops={"file_name": "gin_trgm_ops"}),
        Index("idx_black_hash_trgm", hash,
              postgresql_using='gin', postgresql_ops={"hash": "gin_trgm_ops"})
    )

class DataBaseWork:
    """Класс, который описывает методы создания данных в таблице,
    а так же методы позволяющие работать с таблицей"""

    def __init__(self):
        self.engine = engine
        self.SessionLocal = sessionmaker(bind=engine)

    def has_data(self):
        """Выполняет проверку, существуют ли данные в таблице"""
        db = self.SessionLocal()
        try:
            white_count = db.query(WhiteList).count()
            black_count = db.query(BlackList).count()
            return white_count > 0 and black_count > 0
        finally:
            db.close()

    def generate_test_data(self, count: int)-> bool:
        """
        Генерирует условные записи, которые используются для тестов
        :param count: кол-во записей для генерации
        :returns:
            True - Данные успешно созданы
            False - Данные не созданы
        """
        db = self.SessionLocal()
        try:
            for i in range(0, count, BATCH_SIZE):
                batch = []
                batch_end = min(i + BATCH_SIZE, count)
                for j in range(i, batch_end):
                    idx = i + j
                    file_hash = hashlib.md5(f"white_{idx}".encode()).hexdigest()
                    file_name = f"file_{idx}.txt"
                    batch.append(WhiteList(hash=file_hash, file_name=file_name))
                db.add_all(batch)
                db.commit()
            logger.info("Добавлено 1 миллион записей в белый лист ")
            for i in range(0, count, BATCH_SIZE):
                batch = []
                batch_end = min(i + BATCH_SIZE, count)
                for j in range(i, batch_end):
                    idx = i + j
                    file_hash = hashlib.md5(f"black_{idx}".encode()).hexdigest()
                    file_name = f"file_{idx}.txt"
                    batch.append(BlackList(hash=file_hash, file_name=file_name))
                db.add_all(batch)
                db.commit()
            logger.info("Добавлено 1 миллион записей в чёрный лист")
            return True
        except Exception as e:
            logger.error(f"Неизвестная ошибка{e}")
            return False
        finally:
            db.close()

    def add_data_in_list(self, type_list: str, file_path: str) -> bool:
        """
        Добавляет в выбранную таблицу файл
        в основном пользуется для тестов
        :param type_list: В какую таблицу добавляем "Black" or "White"
        :param file_path: Путь к файлу
        :return:
            bool: True - Если успешно создан, False - Если добавить не получилось
        """
        models = {"Black": BlackList, "White": WhiteList}
        table_class = models.get(type_list)
        if not table_class:
            logger.error("Неизвестный тип списка, используйте black или white")
            return False
        try:
            file_path = Path(file_path)
            file_hash = calculate_file_hash(file_path)
            if not file_hash:
                return False
            file_name = file_path.name
            logger.info("Вычислен кэш для добавления файла")
        except Exception as e:
            logger.error(f"Ошибка вычисления кэша {e}")
            return False
        db = self.SessionLocal()
        try:
            # Проверяем, существует ли уже такой файл
            exists = db.query(table_class).filter_by(hash=file_hash).first()
            if exists:
                logger.warning("Файл уже есть в таблице")
                return False
            new_entry = table_class(hash=file_hash, file_name=file_name)
            db.add(new_entry)
            db.commit()
            logger.success("Файл добавлен в таблицу")
            return True
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Ошибка целостности: {e}")
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Ошибка при добавлении: {e}")
            return False
        finally:
            db.close()

    def del_data_in_list(self, type_list: str, file_path: str) -> bool:
        """
        Удаляет в выбранной таблице хэш файла
        в основном пользуется для тестов
        :param type_list: Из какой таблицы удаляем
        :param file_path: Путь к файлу
        :return:
            bool: True - Если успешно удалён, False - Если удалить не получилось
        """
        models = {"Black": BlackList, "White": WhiteList}
        table_class = models.get(type_list)
        if not table_class:
            logger.error("Неизвестный тип списка, используйте black или white")
            return False
        try:
            file_path = Path(file_path)
            file_hash = calculate_file_hash(file_path)
            if not file_hash:
                return False
            logger.info("Вычислен кэш для удаления файла")
        except Exception as e:
            logger.error(f"Ошибка вычисления кэша {e}")
            return False
        db = self.SessionLocal()
        try:
            # Проверяем, существует ли уже такой узел
            entry = db.query(table_class).filter_by(hash=file_hash).first()
            if not entry:
                logger.warning("Файла нет в таблице")
                return False
            db.delete(entry)
            db.commit()
            logger.success("Файл удалён из таблицы")
            return True
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Ошибка целостности: {e}")
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Ошибка при удалении: {e}")
            return False
        finally:
            db.close()

    def search_one_file_in_table(self, file_path: str) -> str | None:
        """Функция, которая ищет файл в обеих таблицах,
        используются для в функции sup_func.
        :param file_path: Путь к файлу
        :returns:
            Black: Если файл найден в black_list
            White: Если файл найден в white_list
            None: Если файл не найден в таблицах
        """
        file_path = Path(file_path)
        file_hash = calculate_file_hash(file_path)
        if not file_hash:
            return None
        db = self.SessionLocal()
        black_entry = db.query(BlackList).filter_by(hash=file_hash).first()
        if black_entry:
            return "Black"
        white_entry = db.query(WhiteList).filter_by(hash=file_hash).first()
        if white_entry:
            return "White"
        return None

    def return_data_from_table(self, model: str, page: int, per_page: int, filters: dict[str, str | None]) \
            -> dict[
        str, Any]:
        """
        Возвращает таблицу данных с пагинацией с возможностью поиска и без поиска
        :param model: Название таблицы,
        :param page: Номер страницы,
        :param per_page: Кол-во записей на одной странице
        :param filters: Словарь в котором содержится настройка поиска, если None выводим без поиска
        :returns:
            dict[str, str|Any]
        """
        db = self.SessionLocal()
        try:
            models = {"Black": BlackList, "White": WhiteList}
            search_model = models.get(model)
            filter_column = filters.get("filter_column")
            filter_value = filters.get("filter_value")
            offset = (page - 1) * per_page
            query = db.query(search_model)
            if filter_column:
                logger.info("Обнаружен filter_column осуществляем поиск")
                column = getattr(search_model, filter_column)
                query = query.filter(column.like(f"%{filter_value}%"))
            count_value = query.count()
            rows = query.order_by(search_model.id.asc()).offset(offset).limit(per_page).all()
            items = [
                {"id": row.id, "file_name": row.file_name, "hash": row.hash}
                for row in rows
            ]
            return {
                "success": True,
                "type": model,
                "items": items,
                "count_value": count_value,
            }
        except Exception as e:
            logger.error(f"Неизвестная ошибка при выводе таблицы{e}")
            return {
                "success": False,
                "message": f"Ошибка при выводе таблицы{e}"
            }
        finally:
            db.close()

    def init_data(self, count: int = ONE_MILLION_WRITES) -> bool:
        """Основной метод инициализации"""
        if self.has_data():
            logger.info("Данные уже существуют, ничего не генерируем")
            return False

        self.generate_test_data(count)
        return True


# Base.metadata.drop_all(bind=engine)
# logger.info("Таблицы удалены")
Base.metadata.create_all(bind=engine)
logger.info("Данные созданы")

SessionLocal = sessionmaker(bind=engine)
db_session = SessionLocal()

if __name__ == "__main__":
    db_init = DataBaseWork()
    db_init.init_data(ONE_MILLION_WRITES)

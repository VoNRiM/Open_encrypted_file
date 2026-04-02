from flask import Flask, request, jsonify
from loguru import logger
from database import DataBaseWork
import time

"""
*Должен быть запрос на вывод данных с таблицы - DONE
*Должна быть реализованна Пагинация - DONE
*Должен быть поиск(опционально) по колонкам hash и file_name - DONE
*Поиск должен быть максимально быстрым посмотреть по логам 
    с помощью времени - DONE
Обязательные параметры:
page - int > 0
per_page - int > 0
необязательные параметры:
filter_column - string всегда либо hash либо file_name 
filter_value - string по какому значению ищем в filter_column
ответ: - DONE
    json{
        "black_list": 
            {
            id:id
            hash:hash
            file_name:file_name
            }
        count (Если не было поиска - Кол-во записей в общем) - DONE
        count (Если был поиск - Кол-во записей подходящих под поиск) - DONE
"""
# curl "http://127.0.0.1:5000/request_black?page=1&per_page=100&filter_column=hash&filter_value=17593"
# curl "http://127.0.0.1:5000/request_black?page=1&per_page=100&filter_column=file_name&filter_value=123456"

BLACK_LIST = "Black"
WHITE_LIST = "White"

db = DataBaseWork()
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/request_white', methods=['GET'])
def read_white_list():
    page = request.args.get("page", type=int)
    if page is None:
        logger.error("параметр page не задан")
        return jsonify({
            "success": False,
            "message": "page - это обязательный параметр"
        }), 400
    elif page <= 0:
        logger.error("параметр page меньше единицы")
        return jsonify({
            "success": False,
            "message": "page должен быть больше единицы"
        }), 400
    per_page = request.args.get("per_page", type=int)
    if per_page is None:
        logger.error("параметр per_page не задан")
        return jsonify({
            "success": False,
            "message": "per_page - это обязательный параметр"
        }), 400
    elif per_page <= 0:
        logger.error("параметр per_page меньше единицы")
        return jsonify({
            "success": False,
            "message": "Per_page должен быть больше 0"
        }), 400
    filter_column = request.args.get("filter_column", default=None)
    if filter_column:
        if filter_column not in ("hash", "file_name"):
            logger.error("Недопустимые параметры для filter_column используйте 'hash' или 'file_name'")
            return jsonify({
                "success": False,
                "message": "Недопустимые параметры для filter_column используйте 'hash' или 'file_name'"
            }), 400
    filter_value = request.args.get("filter_value", default=None)
    filter_param = {
        "filter_column": filter_column,
        "filter_value": filter_value
    }
    start_time = time.time()
    result = db.return_data_from_table(WHITE_LIST, page, per_page, filter_param)
    result_time = time.time() - start_time
    logger.info(f"Запрос был выполнен за {result_time}")
    return jsonify({
        f"{result["type"]}_list": result["items"],
        "count": result["count_value"]
    }), 200


@app.route('/request_black', methods=['GET'])
def read_black_list():
    page = request.args.get("page", type=int)
    if page is None:
        logger.error("параметр page не задан")
        return jsonify({
            "success": False,
            "message": "page - это обязательный параметр"
        }), 400
    elif page <= 0:
        logger.error("параметр page меньше единицы")
        return jsonify({
            "success": False,
            "message": "page должен быть больше единицы"
        }), 400
    per_page = request.args.get("per_page", type=int)
    if per_page is None:
        logger.error("параметр per_page не задан")
        return jsonify({
            "success": False,
            "message": "per_page - это обязательный параметр"
        }), 400
    elif per_page <= 0:
        logger.error("параметр per_page меньше единицы")
        return jsonify({
            "success": False,
            "message": "Per_page должен быть больше 0"
        }), 400
    filter_column = request.args.get("filter_column", default=None)
    if filter_column:
        if filter_column not in ("hash", "file_name"):
            logger.error("Недопустимые параметры для filter_column используйте 'hash' или 'file_name'")
            return jsonify({
                "success": False,
                "message": "Недопустимые параметры для filter_column используйте 'hash' или 'file_name'"
            }), 400
    filter_value = request.args.get("filter_value", default=None)
    filter_param = {
        "filter_column": filter_column,
        "filter_value": filter_value
    }
    start_time = time.time()
    result = db.return_data_from_table(BLACK_LIST, page, per_page, filter_param)
    result_time = time.time() - start_time
    logger.info(f"Запрос был выполнен за {result_time}")
    if result["success"]:
        return jsonify({
            f"{result["type"]}_list": result["items"],
            "count": result["count_value"]
        }), 200
    else:
        return jsonify({
            "success":f"{result["success"]}",
            "message":f"{result["message"]}"
        }), 500

if __name__ == "__main__":
    app.run(debug=True)

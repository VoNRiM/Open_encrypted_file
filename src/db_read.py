from flask import Flask, request, jsonify
from loguru import logger
from database import DataBaseWork
import time

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
        logger.error("Ошибка: параметр page не задан")
        return jsonify({
            "success": False,
            "message": "Ошибка: page - это обязательный параметр"
        }), 400
    elif page <= 0:
        logger.error("Ошибка: параметр page меньше единицы")
        return jsonify({
            "success": False,
            "message": "Ошибка: page должен быть больше единицы"
        }), 400
    per_page = request.args.get("per_page", type=int)
    if per_page is None:
        logger.error("Ошибка: параметр per_page не задан")
        return jsonify({
            "success": False,
            "message": "Ошибка: per_page - это обязательный параметр"
        }), 400
    elif per_page <= 0:
        logger.error("Ошибка: параметр per_page меньше единицы")
        return jsonify({
            "success": False,
            "message": "Ошибка: Per_page должен быть больше 0"
        }), 400
    filter_column = request.args.get("filter_column", default=None)
    if filter_column:
        if filter_column not in ("hash", "file_name"):
            logger.error("Ошибка: Недопустимые параметры для filter_column используйте 'hash' или 'file_name'")
            return jsonify({
                "success": False,
                "message": "Ошибка: Недопустимые параметры для filter_column используйте 'hash' или 'file_name'"
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
    if result["success"]:
        return jsonify({
            f"{result["type"]}_list": result["items"],
            "count": result["count_value"]
        }), 200
    else:
        return jsonify({
            "success": f"{result["success"]}",
            "message": f"{result["message"]}"
        }), 500


@app.route('/request_black', methods=['GET'])
def read_black_list():
    page = request.args.get("page", type=int)
    if page is None:
        logger.error("Ошибка: параметр page не задан")
        return jsonify({
            "success": False,
            "message": "Ошибка: page - это обязательный параметр"
        }), 400
    elif page <= 0:
        logger.error("Ошибка: параметр page меньше единицы")
        return jsonify({
            "success": False,
            "message": "Ошибка: page должен быть больше единицы"
        }), 400
    per_page = request.args.get("per_page", type=int)
    if per_page is None:
        logger.error("Ошибка: параметр per_page не задан")
        return jsonify({
            "success": False,
            "message": "Ошибка: per_page - это обязательный параметр"
        }), 400
    elif per_page <= 0:
        logger.error("Ошибка: параметр per_page меньше единицы")
        return jsonify({
            "success": False,
            "message": "Ошибка: Per_page должен быть больше 0"
        }), 400
    filter_column = request.args.get("filter_column", default=None)
    if filter_column:
        if filter_column not in ("hash", "file_name"):
            logger.error("Ошибка: Недопустимые параметры для filter_column используйте 'hash' или 'file_name'")
            return jsonify({
                "success": False,
                "message": "Ошибка: Недопустимые параметры для filter_column используйте 'hash' или 'file_name'"
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
            "success": f"{result["success"]}",
            "message": f"{result["message"]}"
        }), 500

if __name__ == "__main__":
    app.run(debug=True)

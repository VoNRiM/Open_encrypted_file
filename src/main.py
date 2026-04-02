import os
from loguru import logger
from flask import Flask, request, jsonify, render_template, Response
import sup_func
import base64

logger.add("debug.log",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message} | {function}",
           level="DEBUG",
           rotation="10 MB",
           retention=5,
           encoding="utf-8")

app = Flask(__name__)
@app.route('/')
def home():
    """Домашняя страница для отображения"""
    return render_template("home.html")

app.config["JSON_AS_ASCII"] = False
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

@app.route('/open_file', methods=['POST'])
def open_file()->tuple[Response, int]:
    """Энд-поинт который принимает зашифрованный файл,
    открывает и сохраняет его в папке temp, возвращая разрешён ли доступ,
    статус код и комментарий
    :returns: tuple[Response, int]
    Response:
        {success: Разрешён ли доступ |
        message: Комментарий}
        int: Статус код
    """
    if 'file' not in request.files:
        logger.error("Нет файла в запросе")
        return  jsonify({
            "success" : False,
            "message" : "Нет файла в запросе"
        }), 400

    file = request.files['file']
    if file.filename == '':
        logger.error("Имя файла пустое")
        return  jsonify({
            "success": False,
            "message": "Имя файла пустое"
        }), 400
    # Проверка не равен ли 0 файл
    file.seek(0,os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size == 0:
        logger.error("Файл пустой")
        return jsonify({
            "success": False,
            "message": "Файл пустой"
        }), 400

    password = request.form.get('password', "") #Будет пустой если файл не ввели
    if password == "":
        logger.error("Поле для пароля пустое")
        return jsonify({
            "success" : False,
            "message" : "Поле для пароля пустое"
        }), 400
    if sup_func.is_base64(password):
        logger.error("Пароль не в формате Base 64")
        return jsonify({
            "success": False,
            "message": "Пароль не в формате Base 64",
        }), 400
    clean_password = base64.b64decode(password).decode("utf-8")
    result = sup_func.smart_open(file, clean_password)
    return jsonify({
        "success": result["success"],
        "message": result["message"],
    }),result["code"]


if __name__ == '__main__':
    app.run(debug=True)

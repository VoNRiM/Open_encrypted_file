import os

from flask import Flask, request, jsonify, render_template
import sup_func

app = Flask(__name__)
@app.route('/')
def home():
    """Домашняя страница для отображения"""
    return render_template("home.html")

app.config["JSON_AS_ASCII"] = False
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

@app.route('/open_file', methods=['POST'])
def open_file():
    """Энд-поинт для приёма файла"""
    if 'file' not in request.files:
        return  jsonify({
            "success" : False,
            "message" : "Нет файла в запросе",
            "code" : 18}), 400

    file = request.files['file']
    if file.filename == '':
        return  jsonify({
            "success": False,
            "message": "Имя файла пустое",
            "code": 17}), 400
    # Проверка не равен ли 0 файл
    file.seek(0,os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size == 0:
        return jsonify({
            "success": False,
            "message": "Файл пустой",
            "code": 20}), 400

    #Проверка на пароль. Мб в отдельный файл?
    password = request.form.get('password', "") #Будет пустой если файл не ввели
    if password == "":
        return jsonify({
            "success" : False,
            "message" : "Поле для пароля пустое",
            "code" : 19
        }), 400

    result = (sup_func.smart_open(file, password))
    if result == 0:
        return jsonify({
            "success": True,
            "message": "Файл успешно загружен",
            "code": 0
        }),200
    elif result == 10:
        return jsonify({
            "success": False,
            "message": "Неверный пароль",
            "code": 10
        }),400
    elif result == 11:
        return jsonify({
            "success": False,
            "message": "Невозможно прочитать файл",
            "code": 11
        }),400
    elif result == 12:
        return jsonify({
            "success": False,
            "message": "Ошибка чтения файлов",
            "code": 12
        }),400
    elif result == 15:
        return jsonify({
            "success": False,
            "message": "Пароль не формата base64",
            "code": 15
        }),400
    elif result == 16:
        return jsonify({
            "success": False,
            "message": "Файлу не требуется пароль",
            "code": 16
        }),400
    else:
        return jsonify({
            "success": False,
            "message": "Неизвестная ошибка",
            "code": result
        }),500


if __name__ == '__main__':
    app.run(debug=True)

# Open_encrypted_file
___
### Команда для установки требуемых пакетов ###
    pip install -r requirements.txt
### Команда для запуска сервера ###
    python3 main.py
### Команда для использования Энд-поинта ### 
    curl -X POST http://127.0.0.1:5000/open_file -F "file=@file_path" -F "your_password"
#### где **file_path** это путь до вашего файла, <br> а **your_password** это пароль от вашего файла
### Команда для проведения тестов ###
    pytest
### Команда для запуска сервера проверки файлов в списках ###
    python3 db_read.py
### Команда для использования Энд-поинта для вывода таблицы ###
    curl "http://127.0.0.1:5000/request_black?page=1&per_page=100&filter_column=hash&filter_value=17593"
#### request_black или request_white - В каком списке ищем.
#### page - (обязательный параметр) страницы, которую мы выводим.
#### per_page - (обязательный параметр) кол-во записей на страницы.
#### filter_column - по какому столбцу мы производим поиск может быть либо hash ли file_name.
#### filter_value - значение по которому мы ищем.
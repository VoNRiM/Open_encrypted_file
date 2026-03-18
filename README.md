# Open_encrypted_file
___
### Команда для установки требуемых пакетов ###
    pip install -r requirements.txt
### Команда для запуска сервера ###
    python3 main.py
### Команда для использования Энд-поинта ### 
    curl -X POST http://127.0.0.1:5000/open_file -F "file=@file_path" -F "your_password"
Где **file_path** это путь до вашего файла, <br> а **your_password** это пароль от вашего файла
### Команда для проведения тестов ###
    pytest
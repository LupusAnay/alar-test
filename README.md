**Запуск проекта**

Необходимо запустить локальную версию PostgreSQL (любым удобным способом) и выполнить скрипт инициализации `database/up.sql`

Например, с помощью команды `psql -U <username> -d <database> -a -f ./database/up.sql`

После этого необходимо указать в файле `backend/app/config.py` корректный url для подключения к БД

После этого необходимо запустить
```sh
cd backend
pip3 install -r requirements.txt
uvicorn app.main:app
```
Это не является production-ready конфигурацией, исключительно в целях тестирования
Приложение будет доступно по адресу http://localhost:8000/index.html

Учетные данные для администратора
```
username: root
password: qwerty
```

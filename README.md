# Описание проекта

Данный API, реализованный на базе DjangoRESTFramework, создан для сайта знакомств. Реализованы функции регистрации 
пользователей, отправки симпатии, просмотр всех пользователей или тех, которые соответствуют определенным фильтрам.
Аутентификация пользователей происходит через токены, которые отправляются в заголовках запросов

# Первичная настройка работы проекта, основанного на фреймворке Django + DjangoRESTFramework

## Контракт для API
Подробная документация по API расположена по адресу (проект при этом должен быть запущен):
```http request
    /api/docs/
```
Там же можно и проверить функциональность API

## Установка виртуального окружения и библиотек/пакетов

Установка всех необходимых библиотек производится с использованием файла с зависимостями requirements.txt

Перед установкой пакетов и библиотек, необходимо удостовериться, что все действия происходят внутри виртуального
окружения. Поэтому сначала необходимо его создать (если этого еще не было сделано)

```text
python3 -m venv venv (python3 - unix / python - windows)
```

Данная команда создаст папку venv в папке, откуда была выполнена команда, и в терминале появится запись *(venv)*
Теперь можно выполнить установку всех требуемых для работы библиотек и пакетов.
Для этого необходимо в терминале (находясь в папке, в которой расположен файл requirements.txt) выполнить следующую
команду:

```text
pip install -r requirements.txt
```

## Подготовка базы данных PostgreSQL и создание виртуального окружения переменных

Подключаемся к консоли Postgres, выполнив следующий код (postgres это суперюзер)

```text
sudo -u postgres psql (linux)
psql -U postgres (windows)
```

Создаем базу данных, создаем пользователя, меняем некоторые настройки по рекомендации из документации Django
(кодировка, чтение транзакций и часовой пояс), открываем для нового пользователя все возможности работы с новой БД

```postgresql
CREATE DATABASE db_name;
CREATE USER username WITH PASSWORD 'password';
ALTER ROLE username SET client_encoding TO 'utf8';
ALTER ROLE username SET default_transaction_isolation TO 'read committed';
ALTER ROLE username SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE db_name TO username;
```

В директории вместе с текущим файлом расположен файл ".env.template". Нужно переименовать его в ".env" и переместить
в одну директорию вместе с файлом settings.py, а потом заполнить по принципу:

```dotenv
SECRET_KEY=secret_key_from_django_settings.py
DEBUG=True_or_False
ALLOWED_HOSTS=some_hosts

# в соответствии с созданными пользователем и БД
DB_NAME=name_of_postgresql_db
DB_USER=username_for_access_to_postgresql_db
DB_PASSWORD=password_for_access_to_postgresql_db
DB_HOST=host_for_postgresql_db

# А также необходимо настроить сервер для отправки электронных писем, это необходимо узнать у почтового 
# клиента (gmail, yandex, mail.ru итд)
EMAIL_BACKEND="django backend, for example (django.core.mail.backends.smtp.EmailBackend) or (django.core.mail.backends.console.EmailBackend)"
EMAIL_HOST="host of your mail server, for example (smtp.gmail.com)"
EMAIL_HOST_USER="your e-mail from where the emails will be sent"
EMAIL_HOST_PASSWORD="your password for e-mail. it`s may be secret app password like in gmail or yandex"
EMAIL_PORT="email port, for example (465)"
EMAIL_USE_SSL=True_or_False
```

В файле settings.py необходимо проверить следующие строчки:

```python
# вверху файла добавить два импорта
import os
import environ

env = environ.Env()
environ.Env.read_env()

# В соответствии с названиями переменных (выше) нужно внести правки в указанные ниже строчки
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': ''
    }
}

EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_SSL = env('EMAIL_USE_SSL')

```

В репозитории уже находится папка staticfiles, которая аккумулирует все статические файлы со всех приложений, но при
расширении проекта и при добавлении новых статических файлов, важно выполнять команду 
```text
python3 manage.py collectstatic (python3 - unix / python - windows)
```

# Примеры запросов через curl

## Регистрация

Запрос:
```text
curl 
-X POST http://127.0.0.1:8000/api/clients/create/
-H "Content-Type: multipart/form-data"
-F "avatar_src=@C:\Users\Никита\Desktop\gangster.jpg;type=image/jpeg"
-F "first_name=Nikita"
-F "last_name=Orlov"
-F "email=t@t.ru"
-F "sex=Men"
-F "avatar_alt=test"
-F "password1=zerozero1"
-F "password2=zerozero1"
-F "username=Nikita"
```

Ответ:
```text
{"Your token for authentication":"613b78cfc4ae67614ec43689e1400f077439cwcb"}
```

## Запрос токена

Запрос:
```text
curl 
-X POST http://127.0.0.1:8000/api/api-token-auth/ 
-H "Content-Type: application/json" 
-d "{\"username\": \"Nikita\", \"password\": \"zerozero1\"}"
```

Ответ:
```text
{"token":"613b78cfc4ae67614ec43689e1400f077439cwcb"}
```

## Отправка симпатии

Запрос:
```text
curl 
-X POST http://127.0.0.1:8000/api/clients/2/match/ 
-H "Authorization: Token 613b78cfc4ae67614ec43689e1400f077439cwcb"
```

Ответ (один из перечисленных). В случае взаимной симпатии на почты пользователей отправляется соответствующее письмо:
```text
{"error": "Not found requested user"}
{"detail": "You have already sent a sympathy to this user"}
{"match": f"You have mutual sympathy! Rather, write to the mail to get to know each other better! "
          f"Sent HI-email for {second_side.like_from_user.first_name} to -> {second_side.like_from_user.email}"}
{"detail": "Sympathy sent to user"}
```

## Просмотр доступных пользователей

Запрос:
```text
curl 
-X 'GET' 'http://127.0.0.1:8000/api/list/' 
-H 'Authorization: Token 613b78cfc4ae67614ec43689e1400f077439cwcb'
```

Ответ:

В ответе будет содержаться список доступных пользователей. Помимо этого в запросе также можно применять фильтры, которые
помогут отфильтровать список пользователей.
Доступные фильтры (параметры, которые нужно указывать в строке запроса):
- first_name - Имя
- last_name - Фамилия
- sex - Пол
- distance - Радиус поиска в КМ
- page - Страница, которую необходимо открыть (пагинация)
- limit - Количество записей за раз

К примеру запрос со всеми параметрами будет выглядеть так:
```text
curl 
-X 'GET' 'http://127.0.0.1:8000/api/list/?first_name=Nikita&last_name=Orlov&sex=Men&distance=10&page=1&limit=20' 
-H 'Authorization: Token 613b78cfc4ae67614ec43689e1400f077439cwcb'
```
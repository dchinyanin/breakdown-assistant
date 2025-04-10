# Ассистент по поломкам

Простое веб-приложение на Flask для учета поломок оборудования на заводе.

## Функционал (MVP)

*   Регистрация и аутентификация пользователей.
*   Добавление записей о поломках (Завод, Линия, Машина, Дата, Описание проблемы/решения/комментарий, Фото).
*   Просмотр списка всех записей.
*   Фильтрация записей по различным критериям.
*   Загрузка фотографий к записям.

## Установка и запуск

1.  **Клонировать репозиторий (или скачать ZIP):**
    ```bash
    # Пока не нужно, так как работаем локально
    # git clone https://github.com/dchinyanin/breakdown-assistant.git
    # cd breakdown-assistant
    ```

2.  **Создать и активировать виртуальное окружение:**
    ```bash
    python -m venv venv
    # Windows PowerShell:
    .\venv\Scripts\Activate.ps1
    # Windows CMD:
    # venv\Scripts\activate.bat
    # macOS/Linux:
    # source venv/bin/activate
    ```

3.  **Установить зависимости:**
    ```bash
    pip install Flask Flask-SQLAlchemy Flask-WTF WTForms-SQLAlchemy Flask-Login email-validator click Werkzeug Jinja2 itsdangerous
    # Или лучше создать requirements.txt (см. ниже) и выполнить:
    # pip install -r requirements.txt
    ```

4.  **Создать базу данных и заполнить справочники:**
    *(Примечание: Убедитесь, что переменная FLASK_APP установлена)*
    ```bash
    # Windows PowerShell: $env:FLASK_APP = "app.py"
    # Windows CMD: set FLASK_APP=app.py
    # macOS/Linux: export FLASK_APP="app.py"

    # Создаем таблицы (если файла *.db нет)
    flask shell
    >>> from app import db
    >>> db.create_all()
    >>> exit()

    # Заполняем справочники Factory, Line, Machine
    flask seed-db
    ```

5.  **Запустить приложение:**
    ```bash
    python app.py
    ```

6.  Открыть [http://127.0.0.1:5000](http://127.0.0.1:5000) в браузере.

## Технологии

*   Backend: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
*   Frontend: HTML, CSS (базовый), Jinja2
*   База данных: SQLite

---

*Заметка: Чтобы другие могли легко установить зависимости, рекомендуется создать файл `requirements.txt`. Для этого в активном окружении `venv` выполните команду:*
```bash
pip freeze > requirements.txt
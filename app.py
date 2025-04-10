import click # Добавляем click
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_ # !!! Импортируем or_ !!!
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os
from forms import RegistrationForm, LoginForm
from werkzeug.utils import secure_filename # Для безопасных имен файлов
from datetime import datetime # На всякий случай
from flask_login import login_required, current_user # Убедись, что они есть
import os

# Импортируем ВСЕ формы
from forms import RegistrationForm, LoginForm, BreakdownForm

# Создаем объект SQLAlchemy, передавая ему наше приложение
db = SQLAlchemy()
login_manager = LoginManager() # Пустой объект login_manager

# Определяем базовую директорию проекта
basedir = os.path.abspath(os.path.dirname(__file__))

# Создаем экземпляр нашего веб-приложения
app = Flask(__name__)

# --- Настройки для SQLAlchemy ---
app.config['SECRET_KEY'] = 'your-very-secret-key' 
# 2. Путь к файлу нашей базы данных SQLite
#    Он будет создан в корне проекта под именем 'breakdowns.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'breakdowns.db')

# 3. Отключаем отслеживание модификаций объектов SQLAlchemy (экономит ресурсы)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# --- Конец настроек SQLAlchemy ---

# --- Настройка папки для загрузок ---
# Путь к папке uploads внутри папки static
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Создаем папку, если её нет
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# --- Конец настройки папки для загрузок ---

# !!! ВЫЗЫВАЕМ init_app() ЗДЕСЬ !!!
db.init_app(app)
login_manager.init_app(app)

# --- Настройка Flask-Login ---
from flask_login import LoginManager # Убедись, что импорт есть

login_manager = LoginManager()
login_manager.init_app(app) # Инициализируем Flask-Login для нашего приложения
login_manager.login_view = 'login'
# Сообщение, которое будет показано пользователю при перенаправлении на страницу входа
login_manager.login_message = "Пожалуйста, войдите в систему, чтобы получить доступ к этой странице."
login_manager.login_message_category = "info" # Категория для flash-сообщений (позже объясню)

@login_manager.user_loader
def load_user(user_id):
    """Эта функция используется Flask-Login для загрузки пользователя из БД по ID,
       который хранится в сессии."""
    # user_id приходит как строка, преобразуем его в integer для запроса к БД
    return User.query.get(int(user_id))

# --- Конец настройки Flask-Login ---

# --- Определение Моделей Базы Данных ---
class Factory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    # Связь 'один ко многим' с записями (один завод - много записей)
    breakdowns = db.relationship('Breakdown', backref='factory_obj', lazy=True)

    def __repr__(self):
        return f'<Factory {self.name}>'

class Line(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    breakdowns = db.relationship('Breakdown', backref='line_obj', lazy=True)

    def __repr__(self):
        return f'<Line {self.name}>'

class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    breakdowns = db.relationship('Breakdown', backref='machine_obj', lazy=True)

    def __repr__(self):
        return f'<Machine {self.name}>'

# --- Определение Моделей Базы Данных ---

# Модель Пользователя
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256)) # Увеличили длину
    full_name = db.Column(db.String(100), nullable=False)
    breakdowns = db.relationship('Breakdown', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

# Модель Поломки
class Breakdown(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Уникальный ID записи
    factory_id = db.Column(db.Integer, db.ForeignKey('factory.id'), nullable=False) # Завод
    line_id = db.Column(db.Integer, db.ForeignKey('line.id'), nullable=False) # Линия
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'), nullable=False) # Машина
    problem_date = db.Column(db.Date, nullable=False) # Дата проблемы (только дата)
    problem_description = db.Column(db.Text, nullable=False) # Описание проблемы
    solution_description = db.Column(db.Text, nullable=True) # Описание решения (может быть пустым)
    comment = db.Column(db.Text, nullable=True) # Комментарий (может быть пустым)
    photo_filename = db.Column(db.String(200), nullable=True) # Имя файла фото (может быть пустым)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp()) # Дата создания записи
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Внешний ключ к таблице user

    def __repr__(self):
        # Метод для представления объекта Breakdown в виде строки
        return f'<Breakdown ID {self.id} on Factory {self.factory_id} / Line {self.line_id} / Machine {self.machine_id}>'

# --- Главный Маршрут ---

@app.route('/')
def index():
    """Отображает главную страницу с использованием HTML-шаблона."""
    title = "Ассистент по поломкам - Главная"
    # Передаем шаблон для рендеринга
    return render_template('index.html', page_title=title)


# --- Маршруты Аутентификации ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    # Добавим вывод перед проверкой формы
    print(f"Request method: {request.method}")
    if request.method == 'POST':
        print(f"Form data received: Full Name={form.full_name.data}, Email={form.email.data}")

    if form.validate_on_submit():
        print("--- Form validation successful ---") # <-- Добавим сюда

        # !!! Проверка на существующего пользователя !!!
        print(f"Checking for existing email: {form.email.data}") # <-- Добавим сюда
        existing_user = User.query.filter_by(email=form.email.data).first()
        print(f"Result of check: existing_user = {existing_user}") # <-- Добавим сюда

        if existing_user:
            print("!!! Email exists, attempting to flash and redirect !!!") # <-- Добавим сюда
            flash('Этот email уже используется. Пожалуйста, выберите другой или войдите.', 'warning')
            return redirect(url_for('register'))
        else:
            print("--- Email does not exist, proceeding to create user ---") # <-- Добавим сюда
            # Создаем нового пользователя
            user = User(
                full_name=form.full_name.data,
                email=form.email.data
            )
            user.set_password(form.password.data)

            print("Adding user to session...") # <-- Добавим сюда
            db.session.add(user)
            print("Committing session...") # <-- Добавим сюда
            try:
                db.session.commit()
                print("--- User successfully committed ---") # <-- Добавим сюда
                flash(f'Аккаунт для {form.full_name.data} успешно создан! Теперь вы можете войти.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                print(f"!!! ERROR during commit: {e}") # <-- Добавим на всякий случай
                db.session.rollback() # Откатываем сессию при ошибке
                flash('Произошла ошибка при создании пользователя.', 'danger')
                return redirect(url_for('register'))

    elif request.method == 'POST':
        # Если метод POST, но валидация не прошла
         print(f"--- Form validation FAILED. Errors: {form.errors} ---") # <-- Добавим сюда

    return render_template('register.html', title='Регистрация', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Обрабатывает вход пользователей."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm() # Создаем экземпляр формы входа

    if form.validate_on_submit():
        # Ищем пользователя в БД по email
        user = User.query.filter_by(email=form.email.data).first()

        # Проверяем, найден ли пользователь и правильный ли пароль
        if user and user.check_password(form.password.data):
            # Логиним пользователя с помощью Flask-Login
            # remember=form.remember.data запомнит сессию, если галочка установлена
            login_user(user, remember=form.remember.data)

            # flash(f'Добро пожаловать, {user.full_name}!', 'success') # Можно добавить приветствие

            # Проверяем, пытался ли пользователь зайти на какую-то страницу до логина
            next_page = request.args.get('next')
            # Перенаправляем на запрошенную страницу или на главную
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            # Если пользователь не найден или пароль неверный
            flash('Неверный email или пароль.', 'danger') # 'danger' - категория ошибки

    return render_template('login.html', title='Вход', form=form)

@app.route('/logout')
def logout():
    """Обрабатывает выход пользователя."""
    logout_user() # Функция Flask-Login для выхода
    flash('Вы успешно вышли из системы.', 'info') # 'info' - категория информационного сообщения
    return redirect(url_for('index'))

# --- Маршруты Приложения ---

# Маршрут для добавления новой записи (защищен @login_required)
@app.route('/add', methods=['GET', 'POST'])
@login_required # Этот декоратор требует, чтобы пользователь был залогинен
def add_breakdown():
    with app.app_context():
        form = BreakdownForm() # Создаем экземпляр формы ВНУТРИ контекста

# --- !!! ДИНАМИЧЕСКИ ЗАПОЛНЯЕМ CHOICES !!! ---
    # Получаем списки объектов из БД
    factories = Factory.query.order_by(Factory.name).all()
    lines = Line.query.order_by(Line.name).all()
    machines = Machine.query.order_by(Machine.name).all()

    # Формируем списки кортежей (value, label) для choices
    factory_choices = [(f.id, f.name) for f in factories]
    line_choices = [(ln.id, ln.name) for ln in lines]
    machine_choices = [(m.id, m.name) for m in machines]

    # Присваиваем choices форме
    form.factory.choices = factory_choices
    form.line.choices = line_choices
    form.machine.choices = machine_choices

    # Добавляем пустой вариант в начало каждого списка
    form.factory.choices.insert(0, (0, '-- Выберите завод --')) # Используем 0 как невалидный ID
    form.line.choices.insert(0, (0, '-- Выберите линию --'))
    form.machine.choices.insert(0, (0, '-- Выберите машину --'))
    # --- !!! КОНЕЦ ЗАПОЛНЕНИЯ CHOICES !!! ---


    if form.validate_on_submit():
        # --- Обработка данных формы ---
        factory = form.factory.data
        line = form.line.data
        machine = form.machine.data
        problem_date = form.problem_date.data
        problem_description = form.problem_description.data
        solution_description = form.solution_description.data
        comment = form.comment.data

        # --- Обработка загрузки файла ---
        photo_filename = None # По умолчанию фото нет
        photo_file = form.photo.data
        if photo_file:
            # Генерируем безопасное имя файла
            filename = secure_filename(photo_file.filename)
            # Можно добавить уникальный префикс, чтобы избежать перезаписи файлов
            # timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            # filename = f"{timestamp}_{filename}"

            # Сохраняем файл в папку uploads
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                photo_file.save(file_path)
                photo_filename = filename # Сохраняем только имя файла для БД
                print(f"Photo saved: {file_path}") # Отладка
            except Exception as e:
                print(f"Error saving photo: {e}") # Отладка
                flash('Ошибка при сохранении фото.', 'danger')
                # Решаем, что делать дальше - прервать или продолжить без фото
                # Пока продолжим без фото
                photo_filename = None

# --- Проверяем тип даты перед созданием объекта ---
        print(f"--- Saving problem_date: {problem_date} (type: {type(problem_date)})")
        
        # --- Создание объекта Breakdown ---
        new_breakdown = Breakdown(
        factory_id=factory,     # <-- ИСПРАВЛЕНО
        line_id=line,          # <-- ИСПРАВЛЕНО
        machine_id=machine,   # <-- ИСПРАВЛЕНО
        problem_date=problem_date,
        problem_description=problem_description,
        solution_description=solution_description,
        comment=comment,
        photo_filename=photo_filename,
        author=current_user
    )

        # --- Сохранение в БД ---
        try:
            db.session.add(new_breakdown)
            db.session.commit()
            flash('Запись о поломке успешно добавлена!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при сохранении записи в БД: {e}', 'danger')
            print(f"DB Commit Error: {e}")
            # Вернем на страницу добавления, чтобы пользователь мог исправить
            return redirect(url_for('add_breakdown'))

    # Если GET-запрос или форма не прошла валидацию
    elif request.method == 'POST':
         print(f"--- Add Breakdown Form validation FAILED. Errors: {form.errors} ---") # Отладка

    return render_template('add_breakdown.html', title='Добавить запись', form=form)

# Маршрут для просмотра всех записей (защищен @login_required)
@app.route('/breakdowns')
@login_required
def view_breakdowns():
    """Отображает список записей о поломках с учетом фильтров."""

    # --- Получаем значения фильтров из GET-параметров URL ---
    factory_id_filter = request.args.get('factory_id', None) # None если параметр отсутствует
    line_id_filter = request.args.get('line_id', None)
    machine_id_filter = request.args.get('machine_id', None)
    problem_date_filter = request.args.get('problem_date', None)
    user_id_filter = request.args.get('user_id', None)
    search_filter = request.args.get('search', None)


    # --- Строим базовый запрос к БД ---
    query = Breakdown.query # Начинаем с запроса ко всем Breakdown

     # --- Применяем фильтры (используем _id) ---
    if factory_id_filter:
        try:
            # Фильтруем по factory_id
            query = query.filter(Breakdown.factory_id == int(factory_id_filter))
        except ValueError:
             flash('Неверный ID завода в фильтре.', 'warning')
    if line_id_filter:
        try:
            # Фильтруем по line_id
            query = query.filter(Breakdown.line_id == int(line_id_filter))
        except ValueError:
             flash('Неверный ID линии в фильтре.', 'warning')
    if machine_id_filter:
        try:
            # Фильтруем по machine_id
            query = query.filter(Breakdown.machine_id == int(machine_id_filter))
        except ValueError:
             flash('Неверный ID машины в фильтре.', 'warning')
    if problem_date_filter:
        # Добавляем отладочные выводы ВНУТРИ этого if
        print(f"--- Date filter received from URL: {problem_date_filter} (type: {type(problem_date_filter)})")
        try:
            date_obj = datetime.strptime(problem_date_filter, '%Y-%m-%d').date()
            print(f"--- Parsed date object: {date_obj} (type: {type(date_obj)})")
            # Применяем фильтр
            query = query.filter(Breakdown.problem_date == date_obj)
            print(f"--- Date filter applied to query ---")
        except ValueError:
            print("!!! Date parsing failed !!!")
            flash('Неверный формат даты в фильтре.', 'warning')
    if user_id_filter:
        try:
            user_id_int = int(user_id_filter)
            query = query.filter(Breakdown.user_id == user_id_int)
        except ValueError:
             flash('Неверный ID пользователя в фильтре.', 'warning')
    if search_filter:
        # Ищем search_filter в любом из трех текстовых полей (регистронезависимо)
        search_term = f"%{search_filter}%" # Добавляем % для поиска подстроки
        query = query.filter(or_(
            Breakdown.problem_description.ilike(search_term),
            Breakdown.solution_description.ilike(search_term),
            Breakdown.comment.ilike(search_term)
        ))

    # --- Получаем список пользователей для фильтра ---
    # (Нужно передать в шаблон, чтобы заполнить выпадающий список)
    users_list = User.query.order_by(User.full_name).all()
    factories_list = Factory.query.order_by(Factory.name).all() # Получаем список заводов
    lines_list = Line.query.order_by(Line.name).all()          # Получаем список линий
    machines_list = Machine.query.order_by(Machine.name).all() # Получаем список машин

    # --- Сортируем и выполняем итоговый запрос ---
    filtered_breakdowns = query.order_by(Breakdown.created_at.desc()).all()

    # --- Передаем данные в шаблон ---
    return render_template('view_breakdowns.html',
                           title='Просмотр записей',
                           breakdowns=filtered_breakdowns,
                           users_list=users_list,
                           factories=factories_list, # Передаем список заводов
                           lines=lines_list,         # Передаем список линий
                           machines=machines_list    # Передаем список машин
                          )

@app.cli.command('seed-db')
def seed_db_command():
    """Заполняет справочные таблицы начальными данными."""
    print("--- Seeding Database ---")

    # --- 1. Добавляем Заводы (из CSV) ---
    factories_to_add = [
        'Аква Стар',
        'Завод Святой Источник',
        'Компания Чистая Вода',
        'Эдельвейс'
    ] # Список заводов из вашего файла
    print("Adding Factories...")
    added_count = 0
    skipped_count = 0
    for factory_name in factories_to_add:
        # Проверяем существование перед добавлением
        exists = Factory.query.filter_by(name=factory_name).first()
        if not exists:
            try:
                new_factory = Factory(name=factory_name)
                db.session.add(new_factory)
                db.session.flush() # Проверка на ранние ошибки
                added_count += 1
            except Exception as e:
                db.session.rollback()
                print(f"Error adding factory '{factory_name}': {e}")
                skipped_count += 1 # Считаем как пропущенный из-за ошибки
        else:
            skipped_count += 1
    try:
        db.session.commit()
        print(f"Factories committed. Added: {added_count}, Skipped (already exist or error): {skipped_count}")
    except Exception as e:
        db.session.rollback()
        print(f"Error during final commit for factories: {e}")
        return # Выходим, если финальный коммит не удался

    # --- 2. Добавляем Линии (из CSV) ---
    lines_to_add = [
        'Alon',
        'Bardi 19',
        'Bardi 5',
        'Cortellazzi',
        'Gallardo',
        'KHS',
        'Kosme',
        'Krones',
        'Krones APET',
        'Line 5',
        'Nate',
        'Parmatec',
        'Synhro',
        'Tech Long',
        'Водоподготовка', # Присутствует и как машина
        'Компрессоры',    # Присутствует и как машина
        'Котельная',      # Присутствует и как машина
        'СКО',            # Присутствует и как машина
        'Чиллеры'         # Присутствует и как машина
    ] # Список линий из вашего файла
    print("\nAdding Lines...")
    added_count = 0
    skipped_count = 0
    for line_name in lines_to_add:
        exists = Line.query.filter_by(name=line_name).first()
        if not exists:
            try:
                new_line = Line(name=line_name)
                db.session.add(new_line)
                db.session.flush()
                added_count += 1
            except Exception as e:
                db.session.rollback()
                print(f"Error adding line '{line_name}': {e}")
                skipped_count += 1
        else:
            skipped_count += 1
    try:
        db.session.commit()
        print(f"Lines committed. Added: {added_count}, Skipped (already exist or error): {skipped_count}")
    except Exception as e:
        db.session.rollback()
        print(f"Error during final commit for lines: {e}")
        return

    # --- 3. Добавляем Машины (из CSV + 'Другая') ---
    machines_to_add = [
        'Автомат розлива',
        'Водоподготовка',      # Присутствует и как линия
        'Выдувная машина',
        'Инспектор',
        'Кейсовая агрегация',
        'Компрессоры',         # Присутствует и как линия
        'Конвейер бутылок',
        'Конвейер упаковок',
        'Котельная',           # Присутствует и как линия
        'Миксер',
        'Обмотчик',
        'Паллетайзер',
        'Паллетная агрегация',
        'СКО',                 # Присутствует и как линия
        'Сериализация бутылок',
        'Термоусадочный автомат', # Было в CSV для Bardi 19
        'Укупорочный автомат',
        'Упаковщик',
        'Устройство обмыва бутылок', # Было в CSV для Bardi 19
        'Чиллеры',             # Присутствует и как линия
        'Этикеровщик',
    ] # Список машин
    print("\nAdding Machines...")
    added_count = 0
    skipped_count = 0
    for machine_name in machines_to_add:
        exists = Machine.query.filter_by(name=machine_name).first()
        if not exists:
            try:
                new_machine = Machine(name=machine_name)
                db.session.add(new_machine)
                db.session.flush()
                added_count += 1
            except Exception as e:
                db.session.rollback()
                print(f"Error adding machine '{machine_name}': {e}")
                skipped_count += 1
        else:
            skipped_count += 1
    try:
        db.session.commit()
        print(f"Machines committed. Added: {added_count}, Skipped (already exist or error): {skipped_count}")
    except Exception as e:
        db.session.rollback()
        print(f"Error during final commit for machines: {e}")
        return

    print("\n--- Database seeding finished successfully! ---")

# --- Запуск приложения ---
if __name__ == '__main__':
  app.run(debug=True)
from flask_wtf import FlaskForm
# Добавляем новые типы полей и FileAllowed, FileRequired для файлов
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, DateField
from flask_wtf.file import FileField, FileAllowed, FileRequired # Для загрузки файлов
# Валидаторы оставляем те же, но добавим Optional
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from flask_wtf.file import FileField, FileAllowed
from wtforms import SelectField

# --- Форма Регистрации ---
class RegistrationForm(FlaskForm):
    full_name = StringField('Полное имя',
                           validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

# --- Форма Входа ---
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

# --- Форма Добавления Поломки ---
class BreakdownForm(FlaskForm):

    # --- Возвращаем SelectField ---
    factory = SelectField(
        'Завод',
        coerce=int, # !!! Преобразуем значение в int !!!
        validators=[DataRequired(message="Выберите завод.")] # Сообщение об ошибке
        # choices будет установлен в app.py
    )

    line = SelectField(
        'Линия',
        coerce=int, # !!! Преобразуем значение в int !!!
        validators=[DataRequired(message="Выберите линию.")]
        # choices будет установлен в app.py
    )

    machine = SelectField(
        'Машина',
        coerce=int, # !!! Преобразуем значение в int !!!
        validators=[DataRequired(message="Выберите машину.")]
        # choices будет установлен в app.py
    )

# Поля даты, описаний, фото и кнопка остаются как были
    problem_date = DateField('Дата проблемы', format='%Y-%m-%d', validators=[DataRequired()])
    problem_description = TextAreaField('Описание проблемы', validators=[DataRequired(), Length(min=10)])
    solution_description = TextAreaField('Описание решения', validators=[Optional(), Length(max=5000)])
    comment = TextAreaField('Комментарий', validators=[Optional(), Length(max=2000)])
    photo = FileField('Прикрепить фото (необязательно)', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Разрешены только изображения!')
    ])
    submit = SubmitField('Сохранить запись')
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=3, max=100)])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), Length(min=4)])
    remember = BooleanField('Ghi nhớ')
    submit = SubmitField('Đăng nhập')

class RegisterForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=3, max=100)])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), Length(min=4)])
    confirm = PasswordField('Nhập lại mật khẩu', validators=[DataRequired(), EqualTo('password', message='Mật khẩu không khớp')])
    employee_name = StringField('Tên nhân viên', validators=[DataRequired(), Length(min=1, max=255)])
    employee_role = StringField('Chức vụ nhân viên (ví dụ: Manager, Receptionist)', default='Receptionist')
    submit = SubmitField('Đăng ký')
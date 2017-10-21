from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from  wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


# 用户登陆表单
class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[Required()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


# 用户注册表单
class RegistrationForm(FlaskForm):
    email = StringField('请输入您的邮箱', validators=[Required(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                                     '用户名必须字母开头！仅可包含以下字符：数字、字母、下划线！')])
    password = PasswordField('请输入密码', validators=[Required(), EqualTo('password2', message='Password must match.')])
    password2 = PasswordField('密码确认', validators=[Required()])
    # validation_code=StringField('邀请码',validators=[Required(),Length(6,6),])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已经注册！请直接登录！')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在！')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('请输入您的旧密码', validators=[Required()])
    password = PasswordField("新密码", validators=[
        Required(), EqualTo('password2', message="Password must match.")])
    password2 = PasswordField('确认输入', validators=[Required()])
    submit = SubmitField("更新密码")


class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱地址', validators=[Required(), Length(1, 64), Email()])
    submit = SubmitField('找回密码')


class PasswordResetForm(FlaskForm):
    email = StringField('邮箱地址', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('请输入新密码', validators=[Required()])
    password2 = PasswordField('确认密码', validators=[Required(), EqualTo('password', 'Password must match.')])
    submit = SubmitField('重置密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('邮箱地址错误，请确认是否输入正确！')


class ChangeEmailForm(FlaskForm):
    email = StringField('请输入新邮箱', validators=[Required(), Length(1, 64),
                                                 Email()])
    password = PasswordField('请输入密码', validators=[Required()])
    submit = SubmitField('更新邮箱地址')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已经注册！请重新输入！')

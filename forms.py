from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

class QuizSettingsForm(FlaskForm):
    difficulty = SelectField('难度', choices=[
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难')
    ], validators=[DataRequired()])
    
    operation_type = SelectField('运算类型', choices=[
        ('add', '加法'),
        ('subtract', '减法'),
        ('multiply', '乘法'),
        ('divide', '除法'),
        ('mixed', '混合运算')
    ], validators=[DataRequired()])
    
    question_count = SelectField('题目数量', choices=[
        ('5', '5题'),
        ('10', '10题'),
        ('20', '20题'),
        ('30', '30题')
    ], validators=[DataRequired()])
    
    submit = SubmitField('开始练习')

class AnswerForm(FlaskForm):
    answer = IntegerField('答案', validators=[DataRequired()])
    submit = SubmitField('提交答案')
from flask_wtf import Form
from ..models import Role, User,Score
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Required, Email, ValidationError, Regexp
from flask_pagedown.fields import PageDownField

from wtforms import RadioField


class NameForm(Form):
    name=StringField("What is your name?",validators=[DataRequired()])
    submit=SubmitField('Submit')


class EditProfileForm(Form):
    avatar = FileField('上传头像')
    name = StringField('用户名', validators=[Length(0, 64)])
    school = StringField('学校', validators=[Length(0, 64)])
    major = StringField('专业',validators=[Length(0,64)])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('确定')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('姓名', validators=[Length(0, 64)])
    school = StringField('学校', validators=[Length(0, 64)])
    major = StringField('专业', validators=[Length(0, 64)])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('确认')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(Form):
    # body = TextAreaField('Whats on your mind?', validators=[Required()])
    # 修改为markdown格式的编辑框

    # category = SelectField(u'Category', choices=[('diary','生活笔记'),
    #                                  ('reading-notes','阅读笔记'),
    #                                  ('python','Python'),
    #                                  ('java','Java'),
    #                                  ('linux', 'Linux'),
    #                                  ('machine-learing','机器学习'),
    #                                  ('front-end','Web 前端'),
    #                                  ('other','其他')])
    # category = SelectField(u'Category', coerce=int,choices=[(1, '生活笔记'),
    #                                              (2, '阅读笔记'),
    #                                              (3, 'Python'),
    #                                              (4, 'Java'),
    #                                              (5, 'Linux'),
    #                                              (6, '机器学习'),
    #                                              (7, 'Web 前端'),
    #                                              (8, '其他')])
    # title=StringField('Title',validators=[Required()])

    # body = PageDownField("有什么新鲜事想告诉大家?", validators=[Required()])
    body = TextAreaField(u'有什么新鲜事想告诉大家?', validators=[DataRequired(u'内容不能为空！')])
    type= SelectField('发文类别',choices=[(0,'默认'),
                                      (1, '复习经验'),
                                      (2, '资料专区'),
                                      (3, '政策专区'),])
    submit = SubmitField('发布')


class CommentForm(Form):
    body = StringField('', validators=[Required()])
    submit = SubmitField('Submit')

class ScoreFrom(Form):
    choices=[(1, '师范英语'),
             (2, '学前教育'),
             (3, '日语'),
             (4, '公共事业管理'),
             (5, '工程管理'),
             (6, '金 融 学'),
             (7, '旅游管理'),
             (8, '土木工程'),
             (9, '法学'),
             (10, '会计'),
             (11, '工商管理'),
             (12, '国际贸易'),
             (13, '交通运输'),
             (14, '电气工程'),
             (15, '市场营销'),
             (16, '计算机'),
             (17, '生物科学'),
             (18, '小学教育'),
             (19, '汉语言文学'),
             (20, '高职英语'),
             (21, '电子商务'),
             (22, '机械设计制造'),
             (23, '艺术设计'),
             (24, '临床医学'),
             (25, '护理学'),
             (26, '口腔医学'),
             (27, '药学'),
             (28, '服装设计'),
             (29, '中药'),
             (30, '医学影像学'),
             (31, '中医学'),
             (32, '针灸'),
             (33, '医学检验')]
    major = SelectField('专业',id="query_score",coerce=int, choices=choices)
    submit=SubmitField('查询')


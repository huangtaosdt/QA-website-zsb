
from flask import Flask,render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_moment import Moment
from config import config



db=SQLAlchemy()
mail=Mail()
moment=Moment()
bootstrap=Bootstrap()

def creater_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    #将 main init 中定义定蓝本注册到程序上
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
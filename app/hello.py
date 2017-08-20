# from flask import Flask,render_template,session,redirect,url_for,flash
# from flask_script import Manager,Shell
# from flask_bootstrap import Bootstrap
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash,check_password_hash
# import os
# #配置sqlite数据库
# basedir=os.path.abspath(os.path.dirname(__file__))
#
# app = Flask(__name__)
# app.config['SECRET_KEY']='hard to guess string'
# app.config['SQLALCHEMY_DATABASE_URI']=\
#     'sqlite:///'+os.path.join(basedir,'data.sqlite')
# app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
#
# db=SQLAlchemy(app)
# manager=Manager(app)
# bootstrap=Bootstrap(app)
#
#
# class Role(db.Model):
#     __tablename__='roles'
#     id=db.Column(db.Integer,primary_key=True)
#     name=db.Column(db.String(64),unique=True)
#
#     users=db.relationship('User',backref='role')
#
#     def __repr__(self):
#         return '<Role %r>' % self.name
#
# class User(db.Model):
#     __tablename__='users'
#     id=db.Column(db.Integer,primary_key=True)
#     username=db.Column(db.String(64),unique=True,index=True)
#     password_hash=db.Column(db.String(128))
#     role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
#
#     @property
#     def password(self):
#         raise AttributeError('password is not a readable attribute')
#
#     @password.setter
#     def password(self,password):
#         self.password_hash=generate_password_hash(password)
#
#     def verify_password(self,password):
#         return check_password_hash(self.password_hash,password)
#
#     def __repr__(self):
#         return '<User %r>' % self.username
#
#
#
# def make_shell_context():
#     return dict(app=app,db=db,Role=Role,User=User)
# manager.add_command('shell',Shell(make_context=make_shell_context))
#
#
#
#
#
# @app.route('/user/<name>')
# def user(name):
#     return render_template('user.html',name=name)
#
#
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
#     # manager.run()
#
#
#
#
#
#
#
#
#
#
#
#
#

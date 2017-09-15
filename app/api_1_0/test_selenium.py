from selenium import webdriver
import unittest, threading
from app.models import User, Post, Role
from app import create_app, db


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        # 启动 Firefox try:
        try:
            # cls.client = webdriver.Firefox()
            cls.client = webdriver.Chrome()
        except:
            pass

        # 如果无法启动浏览器，则跳过这些测试
        if cls.client:
            # 创建程序
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()
            # 禁止日志，保持输出简洁
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")
            # 创建数据库，并使用一些虚拟数据填充 db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)

            # 添加管理员
            admin_role = Role.query.filter_by(permissions=0xff).first()
            admin = User(email='john@example.com',
                         username='john', password='cat',
                         role=admin_role, confirmed=True)
            db.session.add(admin)
            db.session.commit()
            # 在一个线程中启动 Flask 服务器
            threading.Thread(target=cls.app.run).start()

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # 关闭 Flask 服务器和浏览器
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()
            # 销毁数据库
            db.drop_all()
            db.session.remove()
            # 删除程序上下文
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

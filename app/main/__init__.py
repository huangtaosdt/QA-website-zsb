from flask import Blueprint

'''
创建蓝本
'''
main=Blueprint('main',__name__)


from . import views,errors
from ..models import Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

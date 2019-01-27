# functools模块的作用：让被装饰器装饰的函数的属性不发生变化。
import functools
from info.models import User
from flask import session, current_app, jsonify, g
from info.utils import response_code


def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        # 根据user_id查询mysql数据库
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
                if not user: 
                    return jsonify(errno=response_code.RET.USERERR, errmsg='查询用户信息失败')
            except Exception as e:
                current_app.logger.error(e)
        # 使用应用上下文对象g，来临时存储用户数据，
        # 把查询结果的user对象，赋值给g的属性存储
        g.user = user

        return f(*args, **kwargs)

    # wrapper.__name__ = f.__name__
    return wrapper
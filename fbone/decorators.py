# -*- coding: utf-8 -*-

from functools import wraps
from flask import abort
from flask.ext.login import current_user
from SimpleAES import SimpleAES

SECRET_KEY = "the social secret"
CLIENT_KEY = "client_key"

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def singleton(class_):
    class class_w(class_):
        _instance = None

        def __new__(cls, *args, **kwargs):
            if class_w._instance is None:
                class_w._instance = super(class_w, cls).__new__(cls, *args, **kwargs)
                class_w._instance._sealed = False
            return class_w._instance

        def __init__(self, *args, **kwargs):
            if self._sealed:
                return
            super(class_w, self).__init__(*args, **kwargs)
            self._sealed = True
    class_w.__name__ = class_.__name__
    return class_w

def check_token(token):
    aes = SimpleAES(SECRET_KEY)
    try:
        decoded = aes.decrypt(token)
        if decoded.split(":")[0] == CLIENT_KEY:
            return True
        return False
    except Exception as ex:
        return False

def require_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request
        token = request.headers.get("token")
        print token
        if token is not None:
            if check_token(token):
                return f(*args, **kwargs)
            else:
                abort(401)
        else:
            abort(401)
    return decorated_function


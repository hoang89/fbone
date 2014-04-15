# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.mail import Mail
mail = Mail()

from flask.ext.cache import Cache
cache = Cache()

from flask.ext.login import LoginManager
login_manager = LoginManager()

from flask.ext.openid import OpenID
oid = OpenID()

from flask.ext.mongoengine import MongoEngine
mongo = MongoEngine()


from flask.ext.restful import Api

from fbone.reader.views import Reader


def init_extensions(app):
    print "init api"
    api = Api(app)
    api.add_resource(Reader, '/reader')



# -*- coding: utf-8 -*-
from flask import Flask
from werkzeug.routing import BaseConverter, ValidationError
from itsdangerous import base64_encode, base64_decode
from bson.objectid import ObjectId
from bson.errors import InvalidId


def decode(value):
    return base64_decode(str(value))


def encode(value):
    return base64_encode(value)


class ObjectIdConverter(BaseConverter):
    """
    Converts string to :class:`~bson.objectid.ObjectId` and
    vise versa::

        @app.route('/users/<ObjectId:user_id>', methods=['GET'])
        def get_user(user_id):
        ...

    To register it in `Flask`, add it to converters dict::
        app.url_map.converters['ObjectId'] = ObjectIdConverter

    Alternative registration way::
        ObjectIdConverter.register_in_flask(app)
    """

    def to_python(self, value):
        try:
            return ObjectId(decode(value))
        except (InvalidId, ValueError, TypeError):
            raise ValidationError()

    def to_url(self, value):
        #if not (value is ObjectId):
        #    return '1'
        return self.encodeURL(value)

    @classmethod
    def encodeURL(cls, value):
        return encode(ObjectId(value).binary)

    @classmethod
    def register_in_flask(cls, flask_app):
        flask_app.url_map.converters['ObjectId'] = cls


__author__ = 'hoangnn'
from mongoengine import StringField, DateTimeField, IntField
from datetime import datetime
from fbone.extensions import mongo as db
from ..utils import JSONModelMixin

def nowUTC():
    return datetime.utcnow()


class Reader(JSONModelMixin,db.Document):
    _ignore = ['created', 'modified']
    uuid = StringField(unique=True)
    os = IntField()
    device_token = StringField()
    created = DateTimeField()
    modified = DateTimeField()

    meta = {
        'indexes': ['uuid'],
        'index_drop_dups': True
    }

    def save(self, *args, **kwarg):
        if not self.created:
            self.created = nowUTC()
        self.modified = nowUTC()
        return super(Reader, self).save(*args, **kwarg)

    @classmethod
    def getByUUID(cls, uuid):
        return cls.objects.get_or_create(uuid=uuid, auto_save=False)

    @classmethod
    def getOrCreate(cls, uuid, os, token):
        reader, created = cls.getByUUID(uuid=uuid)
        if not created:
            return reader
        reader.os = os
        reader.device_token = token
        reader.save()
        return reader
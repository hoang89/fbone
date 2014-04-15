__author__ = 'hoangnn'
from ..extensions import mongo as db
from mongoengine import ListField, StringField, IntField, URLField, DateTimeField, EmbeddedDocument
from mongoengine import  EmbeddedDocumentField, ReferenceField
from datetime import datetime

def nowUTC():
    return datetime.utcnow()

class Category(EmbeddedDocument):
    name = StringField()
    url = URLField()
    type = IntField()


class Provider(db.Document):
    #_ignore = []
    name = StringField()
    url = URLField()
    img = URLField()
    categories = ListField(EmbeddedDocumentField(Category))
    created = DateTimeField()
    modified = DateTimeField()

    def save(self, *args, **kwargs):
        if self.created is None:
            self.created = nowUTC()
        self.modified = nowUTC()
        super(Provider, self).save(*args, **kwargs)


class LocalProvider(db.Document):
    provider = ReferenceField('Provider', dbref=False)
    position = IntField()
    created = DateTimeField()
    modified = DateTimeField()

    def save(self, *args, **kwargs):
        if self.created is None:
            self.created = nowUTC()
        self.modified = nowUTC()
        super(LocalProvider, self).save(*args, **kwargs)

    @classmethod
    def get_all_provider(cls):
        return cls.objects.only('provider', 'position')


class UserProvider(db.Document):
    local_providers = ListField(ReferenceField('LocalProvider', dbref=True))
    reader = ReferenceField('Reader', dbref=False, unique=True)
    created = DateTimeField()
    modified = DateTimeField()

    def save(self, *args, **kwargs):
        if self.created is None:
            self.created = nowUTC()
        self.modified = nowUTC()
        super(UserProvider, self).save(*args, **kwargs)

    @classmethod
    def init_for_user(cls, reader):
        local_providers = LocalProvider.get_all_provider()
        for local_provider in local_providers:
            cls.objects(reader=reader).update(add_to_set__local_providers=local_provider)
        return cls.objects(reader=reader).first()

    @classmethod
    def get_or_create(cls, reader):
        user_provider, created = cls.objects.get_or_create(reader=reader, auto_save=True)
        if created:
            return cls.init_for_user(reader=reader)
        return user_provider
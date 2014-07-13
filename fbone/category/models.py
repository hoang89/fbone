__author__ = 'hoangnn'
from fbone.extensions import mongo as db
from mongoengine import StringField, IntField, DateTimeField, ListField, ReferenceField
from datetime import datetime
ACTIVE = 1
INACTIVE = 0
DELETED = 2

class Category(db.Document):
    name = StringField()
    slug = StringField()
    status = IntField(default=ACTIVE)
    mangas = ListField(ReferenceField('MangaInfo', dbref=False))
    created_at = DateTimeField()
    modified_at = DateTimeField()

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.modified_at = datetime.utcnow()
        return super(Category, self).save(*args, **kwargs)

    @classmethod
    def get_by_name(cls, name):
        return cls.objects(name=name).first()

    def remove_manga(self, manga):
        self.update(pull__mangas=manga)

    def add_manga(self, manga):
        self.update(add_to_set__mangas=manga)

__author__ = 'hoangnn'

from fbone.extensions import mongo as db
from mongoengine import StringField, ListField, IntField, DateTimeField, EmbeddedDocumentField, ReferenceField
from datetime import datetime
ACTIVE = 1
INACTIVE = 0
DELETED = 2

class Link(db.EmbeddedDocument):
    name = StringField()
    pos = IntField()

class ChapterInfo(db.Document):
    manga = ReferenceField('MangaInfo', dbref=False)
    chapter = StringField()
    name = StringField()
    page = IntField()
    avatar = StringField()
    links = ListField(StringField())
    created_at = DateTimeField()

    def to_chapter(self):
        chapter = {
            'chapter': self.chapter,
            'name': self.name,
            'page': self.page,
            'avatar': self.avatar,
            'created': self.created_at,
            'id': str(self.id)
        }
        return chapter
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        return super(ChapterInfo, self).save(*args, **kwargs)

    @classmethod
    def get_next_chapter(cls, manga):
        return cls.objects(manga=manga).order_by('-chapter').first()

class MangaInfo(db.Document):
    name = StringField()
    author = StringField()
    painter = StringField()
    language = StringField(default="EN")
    desc = StringField()
    img = StringField()
    created_at = DateTimeField()
    read_count = IntField(default=0)
    status = IntField(default=ACTIVE)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        return super(MangaInfo, self).save(*args, **kwargs)

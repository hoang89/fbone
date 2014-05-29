__author__ = 'hoangnn'

from fbone.extensions import mongo as db
from mongoengine import StringField, ListField, IntField, DateTimeField, EmbeddedDocumentField, ReferenceField, BooleanField
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
    status = IntField(default=ACTIVE)
    read_count = IntField(default=0)
    created_at = DateTimeField()
    modified_at = DateTimeField()

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
        self.modified_at = datetime.utcnow()
        return super(ChapterInfo, self).save(*args, **kwargs)

    @classmethod
    def get_next_chapter(cls, manga):
        return cls.objects(manga=manga).order_by('-chapter').first()


class MangaInfo(db.Document):
    name = StringField()
    author = StringField()
    painter = StringField()
    language = StringField(default="VN")
    desc = StringField()
    img = StringField()
    state = StringField()
    chapter = IntField()
    comment = StringField()
    history_comment = ListField(StringField())
    sync_links = ListField(StringField())
    original_link = StringField()
    read_count = IntField(default=0)
    status = IntField(default=INACTIVE)
    created_at = DateTimeField()
    modified_at = DateTimeField()

    def to_manga(self):
        return {'id': str(self.id), 'name': self.name, 'author': self.author, 'painter': self.painter,
                'desc': self.desc,
                'img': self.img, 'state': self.state, 'chapter': self.chapter, 'comment': self.comment,
                'read': self.read_count, 'modified': self.modified_at}

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.modified_at = datetime.utcnow()
        return super(MangaInfo, self).save(*args, **kwargs)


class MangaLink(db.Document):
    link = StringField()
    name = StringField()
    img = StringField()
    desc = StringField()
    detail = StringField()
    author = StringField()
    painter = StringField()
    language = StringField(default="VN")
    chapters = ListField(StringField())
    sync_flag = BooleanField(default=False)
    created_at = DateTimeField()
    modified_at = DateTimeField()

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.modified_at = datetime.utcnow()
        return super(MangaLink, self).save(*args, **kwargs)

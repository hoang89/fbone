# -*- coding: utf-8 -*-

from fbone.extensions import mongo as db
from mongoengine import StringField, ListField, IntField, DateTimeField, EmbeddedDocumentField, ReferenceField, \
    BooleanField
from datetime import datetime
import re

ACTIVE = 1
INACTIVE = 0
DELETED = 2

UPDATE = 1
COMPLETED = 2
SHUTDOWN = 0


class Link(db.EmbeddedDocument):
    name = StringField()
    pos = IntField()


class ChapterInfo(db.Document):
    manga = ReferenceField('MangaInfo', dbref=False)
    chapter = IntField()
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

    def detail_json(self):
        chapter = chapter = {
            'chapter': self.chapter,
            'name': self.name,
            'page': self.page,
            'avatar': self.avatar,
            'created': self.created_at,
            'id': str(self.id),
            'links': self.links
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
    other_name = StringField()
    author = StringField()
    painter = StringField()
    language = StringField(default="VN")
    desc = StringField()
    img = StringField()
    state = IntField(default=UPDATE)
    chapter = IntField()
    current_chapter = IntField()
    comment = StringField()
    history_comment = ListField(StringField())
    categories = ListField(ReferenceField('Category', dbref=False))
    slug = StringField()
    source = StringField(default="Sưu tầm")
    translator = StringField()
    original_link = StringField()
    read_count = IntField(default=0)
    status = IntField(default=INACTIVE)
    updated_time = DateTimeField()
    created_at = DateTimeField()
    modified_at = DateTimeField()

    def to_manga(self):
        return {'id': str(self.id), 'name': self.name, 'author': self.author,
                'desc': self.desc,
                'img': self.img, 'state': self.state, 'chapter': self.chapter, 'comment': self.comment,
                'read': self.read_count, 'modified': self.modified_at}

    def Lower(self, s):
        if type(s) == type(u""):
            return s.lower()
        return unicode(s, "utf8").lower().encode("utf8")

    def convert(self, utf8_str):
        INTAB = 'ạảãàáâậầấẩẫăắằặẳẵóòọõỏôộổỗồốơờớợởỡéèẻẹẽêếềệểễúùụủũưựữửừứíìịỉĩýỳỷỵỹđ /[]'
        INTAB = [ch.encode('utf8') for ch in unicode(INTAB, 'utf8')]
        OUTTAB = "a" * 17 + "o" * 17 + "e" * 11 + "u" * 11 + "i" * 5 + "y" * 5 + "d" + "-"*4
        r = re.compile("|".join(INTAB))
        replaces_dict = dict(zip(INTAB, OUTTAB))
        return r.sub(lambda m: replaces_dict[m.group(0)], utf8_str)


    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.modified_at = datetime.utcnow()
        self.slug = self.convert(self.Lower(self.name.encode('utf8')))
        return super(MangaInfo, self).save(*args, **kwargs)


    @classmethod
    def get_by_alpha(cls):
        list_anpha = []
        for char in range(ord('a'), ord('z') + 1):
            list_anpha.append({'key': chr(char), 'value': cls.objects(slug__istartswith=chr(char), status=ACTIVE)[:20]})
        list_anpha.append({'key': '0-9', 'value': cls.objects(slug=re.compile(r'^[0-9]'), status=ACTIVE)})
        return list_anpha


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

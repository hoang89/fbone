__author__ = 'hoangnn'
from fbone.extensions import mongo as db
from mongoengine import StringField, IntField, DateTimeField
from datetime import datetime
ACTIVE = 1
INACTIVE = 0
DELETED = 2

class MCategory(db.Document):
    name = StringField()
    language = StringField(default="EN")
    status = IntField(default=ACTIVE)
    created_at = DateTimeField()

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        return super(MCategory, self).save(*args, **kwargs)

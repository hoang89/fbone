# -*- coding: utf-8 -*-
"""
    Utils has nothing to do with models and views.
"""

import string
import random
import os

from datetime import datetime
import time


# Instance folder path, make it independent.
INSTANCE_FOLDER_PATH = os.path.join('/tmp', 'instance')

ALLOWED_AVATAR_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Form validation

USERNAME_LEN_MIN = 4
USERNAME_LEN_MAX = 25

REALNAME_LEN_MIN = 4
REALNAME_LEN_MAX = 25

PASSWORD_LEN_MIN = 6
PASSWORD_LEN_MAX = 16

AGE_MIN = 1
AGE_MAX = 300

DEPOSIT_MIN = 0.00
DEPOSIT_MAX = 9999999999.99

# Sex type.
MALE = 1
FEMALE = 2
OTHER = 9
SEX_TYPE = {
    MALE: u'Male',
    FEMALE: u'Female',
    OTHER: u'Other',
}

# Model
STRING_LEN = 64


def get_current_time():
    return datetime.utcnow()


def pretty_date(dt, default=None):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    Ref: https://bitbucket.org/danjac/newsmeme/src/a281babb9ca3/newsmeme/
    """

    if default is None:
        default = 'just now'

    now = datetime.utcnow()
    diff = now - dt

    periods = (
        (diff.days / 365, 'year', 'years'),
        (diff.days / 30, 'month', 'months'),
        (diff.days / 7, 'week', 'weeks'),
        (diff.days, 'day', 'days'),
        (diff.seconds / 3600, 'hour', 'hours'),
        (diff.seconds / 60, 'minute', 'minutes'),
        (diff.seconds, 'second', 'seconds'),
    )

    for period, singular, plural in periods:

        if not period:
            continue

        if period == 1:
            return u'%d %s ago' % (period, singular)
        else:
            return u'%d %s ago' % (period, plural)

    return default


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_AVATAR_EXTENSIONS


def id_generator(size=10, chars=string.ascii_letters + string.digits):
    #return base64.urlsafe_b64encode(os.urandom(size))
    return ''.join(random.choice(chars) for x in range(size))


def make_dir(dir_path):
    try:
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
    except Exception, e:
        raise e

from bson import ObjectId
from converters import ObjectIdConverter
import json

class JSONModelMixin(object):
    def _getIgnore(self):
        if hasattr(self, '_ignore'):
            return self._ignore
        return ['_cls', '_types']

    def to_json(self):
        def _convert_dict_to_json(data):
            struct = {}
            # mongo固有のキーとかも残るのでいらないやつを枝切りする
            ignore = self._getIgnore()
            for k in data:
                if k in ignore: continue
                struct[k] = _convert_value_as_json(data[k])
            return struct

        def _convert_list_to_json(data):
            struct = []
            for v in data:
                struct.append(_convert_value_as_json(v))
            return struct

        def _convert_value_as_json(value):
            if isinstance(value, JSONModelMixin):
                return _convert_value_as_json(value.to_mongo())
            if isinstance(value, list):
                return _convert_list_to_json(value)
            elif isinstance(value, dict):
                return _convert_dict_to_json(value)
            elif isinstance(value, datetime):
                return int(time.mktime(value.timetuple()) + value.microsecond / 1e6)
            elif isinstance(value, (unicode, str, int, bool)):
                return value
            elif isinstance(value, ObjectId):
                return ObjectIdConverter.encodeURL(value)
        return json.dumps(_convert_value_as_json(self.to_mongo()))
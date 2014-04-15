__author__ = 'hoangnn'
from ..decorators import singleton
from .models import Reader

@singleton
class ReaderService(object):

    @classmethod
    def getOrCreate(cls, uuid, os, token):
        return Reader.getOrCreate(uuid=uuid, os=os, token=token)
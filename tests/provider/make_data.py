__author__ = 'hoangnn'

from fbone.provider.models import *

def make_provider():
    Provider.drop_collection()
    LocalProvider.drop_collection()
    for i in range(20):
        provider = Provider()
        provider.name = "Provider %d" % (i+1)
        provider.url = "http://google.com.vn/?%d" % (i+1)
        provider.img = "http://google.com.vn/?image=%d" % (i+1)
        provider.save()
        local_provider = LocalProvider()
        local_provider.provider = provider
        local_provider.position = i+1
        local_provider.save()
        print "create: " + str(local_provider.id)
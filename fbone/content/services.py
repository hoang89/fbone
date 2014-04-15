__author__ = 'hoangnn'
from ..decorators import singleton
from bs4 import BeautifulSoup
from fbone.extensions import cache
import requests

@singleton
class ContentService(object):

    @classmethod
    @cache.memoize(6000)
    def parse_link(cls, link):
        headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 4.2.1; Nexus 4 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"}
        html = requests.get(link, headers=headers)
        html.encoding = "utf-8"
        return cls.__vnexpress_parser(html=html)

    @classmethod
    def __vnexpress_parser(cls, html):
        soup = BeautifulSoup(html.text)
        print (soup.title.string).encode("utf-8").strip()
        for tag in soup.find_all("b"):
            if tag.string is not None:
                print (tag.string).encode("utf-8").strip()
        return soup.prettify()
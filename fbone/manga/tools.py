__author__ = 'hoangnn'

from uuid import uuid4
import boto
import md5
import os.path
from models import ChapterInfo, Link
from flask import current_app
from bs4 import BeautifulSoup, Tag, ResultSet
import requests

S3_KEY = 'AKIAI3TIE3E2IY2P5KOA'
S3_SECRET = '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'
S3_UPLOAD_DIRECTORY = 'manga'
S3_BUCKET = 'hoangnn'

import urllib, os, sys


def make_upload_path(filename, folder):
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "manga")
    upload_path = os.path.join(upload_path, folder)
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    return os.path.join(upload_path, filename)


def save_image(url, folder):
    filename = url.split("/").pop()
    #ext = filename.split('.').pop()
    #filename = md5.new(filename).hexdigest() + "." + ext
    path = make_upload_path(filename=filename, folder=folder)
    urllib.urlretrieve(url, path)
    return path


def get_all(chapter, base, max):
    result = []
    for i in range(1, max):
        item = {}
        key = chapter + "_" + str(i) + '.jpg'
        path = save_image(base + str(i) + ".jpg")
        item['path'] = path
        item['key'] = key
        result.append(item)
    return result


def push_picture_to_s3(fn, key):
    try:
        import boto
        from boto.s3.key import Key

        bucket_name = S3_BUCKET
        conn = boto.connect_s3(S3_KEY, S3_SECRET)
        bucket = conn.get_bucket(bucket_name)
        k = Key(bucket)
        k.key = key
        k.set_contents_from_filename(fn)
        #k.make_public()
        os.remove(fn)
    except Exception as e:
        raise e


def pull_picture_from_s3(fn):
    try:
        import boto
        from  boto.s3.key import Key

        bucket_name = S3_BUCKET
        conn = boto.connect_s3(S3_KEY, S3_SECRET)
        bucket = conn.get_bucket(bucket_name)
        k = Key(bucket)
        k.key = fn
        url = k.generate_url(expires_in=300, query_auth=True)
        return url
    except Exception as e:
        return "NULL"


def create_manga(chapter, base, max):
    chapter_name = "chapter" + str(chapter)
    result = get_all(chapter=chapter_name, base=base, max=max)
    chapter_info = ChapterInfo.objects(chapter=chapter).first()
    if not chapter_info:
        chapter_info = ChapterInfo()
    chapter_info.chapter = chapter
    chapter_info.name = chapter_name.capitalize()
    chapter_info.page = max - 1
    links = []
    counter = 0
    for item in result:
        push_picture_to_s3(item['path'], item['key'])
        link = Link()
        link.pos = counter
        link.name = item['key']
        links.append(link)
        counter += 1
    chapter_info.links = links
    ava = links[0]
    chapter_info.avatar = ava.name
    chapter_info.save()


def parse_all():
    base_url = "http://blogtruyen.com/truyen/one-piece/chap-"
    for count in range(1, 10):
        parse_chapter(base_url + str(count), "Chapter" + str(count))


def get_real_url(url):
    url = url.split('?')[0]
    return url


def parse_chapter(url, chapter):
    html = requests.get(url)
    b = BeautifulSoup(html.text)
    results = b.findAll("article", {'id': 'content'})
    for r in results:
        for child in r.children:
            if type(child) is Tag:
                url = get_real_url(child['src'])
                print save_image(url, chapter)

def parse_hkgh():
    url = "http://blogtruyen.com/truyen/hiep-khach-giang-ho"
    html = requests.get(url)
    b = BeautifulSoup(html.text)
    list_chapter = b.find('div', {'id': 'list-chapters'})

__author__ = 'hoangnn'

from bs4 import BeautifulSoup, Tag, ResultSet
import requests
import csv, os, sys
from models import ChapterInfo, MangaInfo, MangaLink
from flask import abort
import urllib


def parse_chapter_links(url):
    html = requests.get(url)
    b = BeautifulSoup(html.text)
    all_links = b.find_all('span', class_='title')
    for link in all_links:
        yield link


def get_output_file(name):
    path = os.path.join(os.getcwd(), name)
    return path


def get_all_chapter_links(url):
    """
    Get all chapter link from url of manga
    """
    base = "http://blogtruyen.com"
    all = []
    for link in parse_chapter_links(url):
        l = link.find('a')
        if l and type(l) is Tag:
            chapter = base + urllib.quote(l.get('href'))
            all.append(chapter)
    return all


def read_chapter_link(path):
    with open(path, 'r') as file:
        for line in file:
            yield line

def parse_chapter(chapter):
    try:
        return int(chapter)
    except:
        return 100000

def get_chapter_file_link(chapter_url):
    """
    Get all chapter info from blog truyen
    chapter_link: link to blog truyen chapter
    """
    #chapter_url = urllib.quote(chapter_url)
    print chapter_url
    chapter_info = {}

    html = requests.get(chapter_url)
    html.encoding = "utf-8"
    b = BeautifulSoup(html.text)
    header = b.find('header')
    h1 = header.find('h1')
    title = h1.text
    chapter_info['name'] = title.strip()
    chapter_number = title.split(" ").pop()
    chapter_info['chapter'] = parse_chapter(chapter_number)
    all_file_link = b.find('article', {'id': 'content'})
    all_imgs = all_file_link.find_all('img')
    links = []
    for img in all_imgs:
        print img.get('src')
        links.append(img.get('src'))
    chapter_info['links'] = links
    chapter_info['page'] = len(links)
    chapter_info['avatar'] = links[0]
    return chapter_info


def parse_all_chapter_to_db(root, manga_id):
    """
    Craw all chapter image from blog truyen and save to database
    """
    all = get_all_chapter_links(root)
    parse_manga_link(all, manga_id)


def parse_manga_link(all, manga_id):
    """
    With each link in all link, craw info from blog truyen and save it to database
    If link was craw before, ignore it
    """
    manga = MangaInfo.objects(id=manga_id).first()
    if manga is None:
        raise RuntimeError("manga not exist")

    counter = 0
    for link in all:
        chapter_info = get_chapter_file_link(link.strip())
        cif = ChapterInfo.objects(name=chapter_info['name'], manga=manga).first()
        if not cif:
            cif = ChapterInfo()
        cif.name = chapter_info['name']
        cif.chapter = chapter_info['chapter']
        cif.avatar = chapter_info['avatar']
        cif.manga = manga
        cif.page = chapter_info['page']
        cif.links = chapter_info['links']
        cif.save()

def add_manga_link(link, manga_id):
    print link
    chapter_info = get_chapter_file_link(link.strip())
    manga = MangaInfo.objects(id=manga_id).first()
    if manga is None:
        raise RuntimeError("manga not exist")

    cif = ChapterInfo.objects(name=chapter_info['name'], manga=manga).first()
    if not cif:
        cif = ChapterInfo()

    cif.name = chapter_info['name']
    cif.chapter = chapter_info['chapter']
    cif.avatar = chapter_info['avatar']
    cif.manga = manga
    cif.page = chapter_info['page']
    cif.links = chapter_info['links']
    cif.save()


# link all manga: http://blogtruyen.com/danhsach/tatca

def parse_all_manga_from_blog_truyen(page):
    """
    Get all available story from blog truyen
    Save story info to database, ignore saved story
    """
    link = "http://blogtruyen.com/ListStory/GetListStory"
    base_link = "http://blogtruyen.com"
    PageIndex = page
    inserted_manga_count = 0

    data = {'Url': 'tatca', 'OrderBy': '3', 'PageIndex': str(PageIndex)}
    html = requests.post(link, data=data)

    print data

    if html.status_code != 200:
        return 'Quit not found at page ' + str(PageIndex) + ' inserted: ' + inserted_manga_count

    b = BeautifulSoup(html.content)
    all_title = b.find_all('span', class_='tiptip fs-12 ellipsis')
    all_content = b.find_all('div', class_='hidden tiptip-content')
    if len(all_title) <= 0:
        return 'Quit empty at page ' + str(PageIndex) + ' inserted: ' + str(inserted_manga_count)

    if len(all_title) != len(all_content):
        return

    for counter in range(0, len(all_title)):
        title = all_title[counter]
        content = all_content[counter]
        if title and content and type(title) is Tag and type(content) is Tag:
            url = title.find('a')
            link = base_link + url.get('href')
            manga = MangaLink.objects(link=link).first()
            if not manga is None:
                continue
            else:
                inserted_manga_count += 1
                manga = MangaLink()
                manga.link = link
                manga.name = url.string.encode('utf-8')
                img = content.find('img')
                manga.img = img.get('src')
                desc = content.find('div', class_='al-j fs-12')
                manga.desc = desc.string.encode('utf-8')
                manga.save()


def parse_all_chapter_from_blog_truyen(manga_id):
    manga_link = MangaLink.objects(id=manga_id).first()
    if manga_link is None:
        return 0
    else:
        all = get_all_chapter_links(manga_link.link)
        manga_link.chapters = all
        manga_link.save()
        return len(all)


def parse_manga_detail_from_blog_truyen(link):
    """
    When we have link to story, we craw detail info of story and save it
    to database
    """
    html = requests.get(link)
    manga_info = {}
    if html.status_code != 200:
        abort(401, 'Cannot get data')
    b = BeautifulSoup(html.text)
    title = b.find('h1', class_='entry-title')
    manga_info['name'] = title.find('a').string.encode('utf-8')
    thumb = b.find('div', class_='thumbnail')
    manga_info['img'] = thumb.find('img').get('src')
    detail = b.find('div', class_='detail')
    content = detail.find('div', class_='content')
    manga_info['detail'] = unicode(content).encode('utf-8')
    desc = b.find('div', class_='description')
    manga_info['desc'] = unicode(desc).encode('utf-8')
    return manga_info


def complete_manga_info(manga_id):
    manga_link = MangaLink.objects(id=manga_id).first()
    link = manga_link.link
    manga_info = parse_manga_detail_from_blog_truyen(link)
    manga_link.desc = manga_info['detail']
    manga_link.detail = manga_info['desc']
    manga_link.img = manga_info['img']
    manga_link.save()

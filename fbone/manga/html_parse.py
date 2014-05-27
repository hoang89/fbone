__author__ = 'hoangnn'

from bs4 import BeautifulSoup, Tag, ResultSet
import requests
import csv, os, sys
from models import ChapterInfo, MangaInfo


def parse_chapter_links(url):
    #url = "http://blogtruyen.com/truyen/hiep-khach-giang-ho"
    html = requests.get(url)
    b = BeautifulSoup(html.text)
    #list_chapter = b.find('div', {'id': 'list-chapters'})
    all_links = b.find_all('span', class_='title')
    for link in all_links:
        yield link


def get_output_file(name):
    path = os.path.join(os.getcwd(), name)
    return path


def get_all_chapter_links(url):
    base = "http://blogtruyen.com"
    path = get_output_file('link.txt')
    with open(path, 'w') as file:
        for link in parse_chapter_links(url):
            l = link.find('a')
            if l and type(l) is Tag:
                chapter = base + l.get('href') + '\n'
                file.write(chapter)
    return path


def read_chapter_link(path):
    with open(path, 'r') as file:
        for line in file:
            yield line


def get_chapter_file_link(chapter_url):
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
    chapter_info['chapter'] = chapter_number
    all_file_link = b.find('article', {'id': 'content'})
    all_imgs = all_file_link.find_all('img')
    links = []
    for img in all_imgs:
        links.append(img.get('src'))
    chapter_info['links'] = links
    chapter_info['page'] = len(links)
    chapter_info['avatar'] = links[0]
    return chapter_info

def parse_manga_link(root, manga_id):
    # Lay tat ca cac chapter link
    path = get_all_chapter_links(root)
    manga = MangaInfo.objects(id=manga_id).first()
    if manga is None:
        raise RuntimeError("manga not exist")
    # voi moi chapter link lay tat ca cac link anh
    # add vao db
    counter = 0
    for link in read_chapter_link(path):
        chapter_info = get_chapter_file_link(link.strip())
        cif = ChapterInfo.objects(name=chapter_info['name']).first()
        if not cif:
            cif = ChapterInfo()
        cif.name = chapter_info['name']
        cif.chapter = chapter_info['chapter']
        cif.avatar = chapter_info['avatar']
        cif.manga = manga
        cif.page = chapter_info['page']
        cif.links = chapter_info['links']
        cif.save()
        """
        counter += 1
        if counter == 10:
            break
        """


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise RuntimeError('Must apply manga id and link')
    root = sys.argv[1]
    manga_id = sys.argv[2]
    parse_manga_link(root, manga_id)


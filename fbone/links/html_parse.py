from bs4 import BeautifulSoup, Tag, ResultSet
import requests
import csv, os, sys
from flask import abort
import urllib

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
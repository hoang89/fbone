__author__ = 'hoangnn'

from bs4 import BeautifulSoup, Tag, ResultSet
import requests
import csv, os, sys

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
    chapter_info['name'] = title
    chapter_number = title.split(" ").pop()
    chapter_info['chapter'] = chapter_number
    all_file_link = b.find('article', {'id': 'content'})
    all_imgs = all_file_link.find_all('img')
    links = []
    for img in all_imgs:
        links.append(img.get('src'))
    #chapter_info['links'] = links
    chapter_info['page'] = len(links)
    chapter_info['avatar'] = links[0]
    return chapter_info

if __name__ == '__main__':
    root = sys.argv[1]
    path = get_all_chapter_links(root)
    #print path
    counter = 0
    for link in read_chapter_link(path):
        chapter_info = get_chapter_file_link(link.strip())
        print chapter_info
        counter += 1
        if counter >= 10:
            break
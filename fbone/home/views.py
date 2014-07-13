__author__ = 'hoangnn'
# -*- coding: utf-8 -*-
from flask.ext.classy import FlaskView, route
from flask import render_template, Blueprint, request, abort
from ..manga.models import MangaInfo, ChapterInfo
from ..category.models import Category
from fbone.utils import pretty_date
ACTIVE = 1
INACTIVE = 0
DELETED = 2

PER_PAGE = 24

UPDATE = 1
COMPLETED = 2
SHUTDOWN = 0

home = Blueprint('home', __name__, template_folder='templates')

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class HomeView(FlaskView):

    route_base = "/"
    route_prefix = "home"

    def _get_page(self):
        try:
            page = int(request.args.get('page',1))
        except:
            page = 1
        return page

    def index(self):
        page = self._get_page()
        top_new = MangaInfo.objects(status=ACTIVE).order_by('-updated_time').paginate(page=1, per_page=12)
        top_read = MangaInfo.objects(status=ACTIVE).order_by('-read_count').paginate(page=1, per_page=12)
        top_chapter = ChapterInfo.objects().order_by('-created_at').paginate(page=1, per_page=150)
        list_alpha = MangaInfo.get_by_alpha()
        categories = Category.objects()
        completed = MangaInfo.objects(status=ACTIVE, state=COMPLETED).order_by('name').paginate(page=page,per_page=PER_PAGE)

        return render_template('home/index.html', top_new=top_new.items, top_read=top_read.items, list_alpha = list_alpha,
                               categories=categories, top_chapter=top_chapter.items, completed=completed.items)

    @route('/manga/<string:slug>')
    def detail(self, slug):
        manga = MangaInfo.objects(slug=slug).first()
        if not manga:
            return abort(404)
        chapters = ChapterInfo.objects(manga=manga)
        return render_template('home/detail.html', manga=manga, chapters=chapters)

HomeView.register(home)

@home.app_template_filter('trim_text')
def trim_text(text):
    return text[0:20]+'...'

@home.app_template_filter('prettydate')
def prettydate(date):
    if date:
        return pretty_date(date)
    else:
        return "NONE"

@home.app_template_filter('state_filter')
def state_filter(state):
    if state == 1:
        return "Đang cập nhật".decode('utf-8')
    if state == 2:
        return "Hoàn thành".decode('utf-8')
    if state is None or state == 0:
         return "Tạm dừng".decode('utf-8')

@home.app_template_filter('unicode_safe')
def unicode_safe(ustring):
    return ustring.decode('utf-8')

@home.app_template_filter('display_time')
def display_time(date):
    if date:
        return date.strftime("%A %d. %B %Y")
    else:
        return "NONE"

@home.app_template_filter('chapter_time')
def chapter_time(date):
    if date:
        return date.strftime("%d - %m")
    else:
        return "NONE"
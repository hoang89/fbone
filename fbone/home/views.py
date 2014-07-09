__author__ = 'hoangnn'

from flask.ext.classy import FlaskView
from flask import render_template, Blueprint, request
from ..manga.models import MangaInfo
from fbone.utils import pretty_date

home = Blueprint('home', __name__, template_folder='templates')

class HomeView(FlaskView):

    route_base = "/"
    route_prefix = "home"
    def index(self):
        top_new = MangaInfo.objects().order_by('-updated_time').paginate(page=1, per_page=12)
        top_read = MangaInfo.objects().order_by('-read_count').paginate(page=1, per_page=12)
        return render_template('home/index.html', top_new=top_new.items, top_read=top_read.items)

HomeView.register(home)

@home.app_template_filter('trim_text')
def trim_text(text):
    return text[0:12]+'...'

@home.app_template_filter('prettydate')
def prettydate(date):
    if date:
        return pretty_date(date)
    else:
        return "NONE"
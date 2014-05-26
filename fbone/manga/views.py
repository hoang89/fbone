__author__ = 'hoangnn'
from flask import Blueprint, render_template, flash, jsonify, redirect, url_for
from tools import create_manga
from forms import InsertForm, MangaForm
from models import ChapterInfo, MangaInfo
from flask.ext.classy import FlaskView, route
manga = Blueprint('manga', __name__, template_folder='templates')
"""

@manga.route('/')
def index():
    return 'Ok created'


@manga.route('/insert', methods=['POST', 'GET'])
def insert():
    form = InsertForm()
    if form.validate_on_submit():
        chapter = form.chapter.data
        base = form.base.data
        max = form.max.data
        create_manga(chapter=chapter, base=base, max=max)
        flash("Success insert new manga")
        return render_template('manga/insert.html', form=form)
    else:
        return render_template('manga/insert.html', form=form)

@manga.route('/all')
def all():
    all = ChapterInfo.objects().exclude('links').order_by('chapter')
    result = []
    for i in all:
        result.append(i.to_chapter())
    return jsonify(res=result)
"""

class MangaView(FlaskView):
    route_base = "manga"

    def index(self):
        items = MangaInfo.objects()
        return render_template('manga/index.html', items=items)

    @route('/create', methods=['GET','POST'])
    def create(self):
        form = MangaForm()
        if form.validate_on_submit():
            manga_info = MangaInfo()
            form.populate_obj(manga_info)
            manga_info.save()
            return redirect(url_for('manga.MangaView:index'))
        else:
            return render_template('manga/create.html', form=form)

    @route('/detail/<string:id>')
    def detail(self, id):
        item = MangaInfo.objects(id=id).first()
        return render_template('manga/detail.html', item=item)



class ChapterView(FlaskView):
    route_base = "chapter"

    @route('/add_vechai/<string:id>')
    def add_vechai(self, id):
        next_chapter = ChapterInfo.get_next_chapter(manga=id)
        print next_chapter
        print '--'*100
        return render_template('chapter/add_vechai.html')

MangaView.register(manga)
ChapterView.register(manga)
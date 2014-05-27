__author__ = 'hoangnn'
from flask import Blueprint, render_template, flash, jsonify, redirect, url_for, request
from tools import create_manga
from forms import InsertForm, MangaForm, InitForm, ChapterEditForm
from models import ChapterInfo, MangaInfo
from flask.ext.classy import FlaskView, route
from datetime import datetime
import urllib
from fbone.utils import pretty_date
from html_parse import parse_manga_link

manga = Blueprint('manga', __name__, template_folder='templates')


class MangaView(FlaskView):
    route_base = "manga"

    def index(self):
        items = MangaInfo.objects()
        return render_template('manga/index.html', items=items)

    @route('/create', methods=['GET', 'POST'])
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

    @route('/edit/<string:id>', methods=['GET', 'POST'])
    def edit(self, id):
        manga_info = MangaInfo.objects(id=id).first()
        form = MangaForm(obj=manga_info)
        if request.method == 'GET':
            return render_template('manga/edit.html', form=form, id=id)
        else:
            form.populate_obj(manga_info)
            manga_info.save()
            return redirect(url_for('manga.MangaView:index'))

    @route('/init/<string:id>', methods=['GET', 'POST'])
    def init(self, id):
        form = InitForm()
        if request.method == 'GET':
            return render_template('manga/init.html', form=form, id=id)
        else:
            url = form.url.data
            parse_manga_link(url, id)
            flash('Success init manga')
            return redirect(url_for('manga.ChapterView:index', id=id))


class ChapterView(FlaskView):
    route_base = "chapter"

    @route('/<string:id>')
    def index(self, id):
        page = int(request.args.get('page', 1))
        pages = ChapterInfo.objects(manga=id).exclude("links").paginate(page=page, per_page=10)
        return render_template('chapter/index.html', items=pages.items, pages=pages, id=id)

    @route('/detail/<string:id>')
    def detail(self, id):
        chapter = ChapterInfo.objects(id=id).first()
        return render_template('chapter/detail.html', chapter=chapter)

    @route('/edit/<string:id>', methods=['GET','POST'])
    def edit(self, id):
        back = request.args.get('back')
        print back
        chapter_info = ChapterInfo.objects(id=id).first()
        form = ChapterEditForm(obj=chapter_info)
        if request.method == 'GET':
            return render_template('chapter/edit.html', form=form, chapter=chapter_info, back=back)
        else:
            chapter_info.name = form.name.data
            chapter_info.page = form.page.data
            chapter_info.avatar = form.avatar.data
            chapter_info.chapter = form.chapter.data
            chapter_info.save()
            return redirect(urllib.unquote(back).decode('utf-8')) if back else redirect(url_for('manga.ChapterView:index', id=chapter_info.manga.id))
            #return redirect(url_for('manga.ChapterView:index', id=chapter_info.manga.id))

    @route('/remove_img/')
    def remove_img(self):
        id = request.args.get('id')
        image = request.args.get('image')
        back = request.args.get('back')
        print id, image
        back = urllib.unquote(back).decode('utf-8')
        return redirect(back)


@manga.context_processor
def utility_processor():
    def format_date(date):
        return pretty_date(date)

    return dict(format_date=format_date)


MangaView.register(manga)
ChapterView.register(manga)
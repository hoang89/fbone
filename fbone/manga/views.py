from fbone.manga.models import MangaLink
from flask import Blueprint, render_template, flash, jsonify, redirect, url_for, request
from tools import create_manga
from forms import InsertForm, MangaForm, InitForm, ChapterEditForm, MangaLinkEditForm
from models import ChapterInfo, MangaInfo
from flask.ext.classy import FlaskView, route
from datetime import datetime
import urllib, requests
from bs4 import BeautifulSoup
from fbone.utils import pretty_date
from html_parse import parse_manga_link, parse_all_manga_from_blog_truyen, parse_all_chapter_from_blog_truyen
from html_parse import complete_manga_info, parse_all_chapter_to_db

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
            parse_all_chapter_to_db(url, id)
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

    @route('/edit/<string:id>', methods=['GET', 'POST'])
    def edit(self, id):
        back = request.args.get('back')
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
            return redirect(urllib.unquote(back).decode('utf-8')) if back else redirect(
                url_for('manga.ChapterView:index', id=chapter_info.manga.id))
            #return redirect(url_for('manga.ChapterView:index', id=chapter_info.manga.id))

    @route('/remove_img/')
    def remove_img(self):
        id = request.args.get('id')
        image = request.args.get('image')
        back = request.args.get('back')
        print id, image
        back = urllib.unquote(back).decode('utf-8')
        return redirect(back)


class MangaLinkView(FlaskView):
    route_base = "links"

    @route('/')
    def index(self):
        page = int(request.args.get('page', 1))
        paginates = MangaLink.objects().paginate(page=page, per_page=10)
        return render_template('links/index.html', paginates=paginates)

    @route('/all')
    def all(self):
        """
        Get all managa from bog truyen
        """
        all = parse_all_manga_from_blog_truyen()
        return jsonify(res=all)

    @route('/all_chapter/<string:id>')
    def all_chapter(self, id):
        """
        Get all chapter link from blog truyen save to database
        """
        back = request.args.get('back')
        if back:
            back = urllib.unquote(back).encode('utf-8')
        all = parse_all_chapter_from_blog_truyen(manga_id=id)
        flash('Success get all ' + str(all) + ' chapter links', 'success')
        return redirect(back) if back else redirect(url_for('manga.MangaLinkView:index'))

    @route('/detail/<string:id>')
    def detail(self, id):
        manga_link = MangaLink.objects(id=id).first()
        if not manga_link.detail:
            flash('Complete manga info first', 'error')
        if not manga_link.chapters:
            flash('Get all chapter first', 'error')
        if not manga_link.author:
            flash('Edit manga info before sync', 'error')
        return render_template('links/detail.html', item=manga_link)

    @route('/complete/<string:id>')
    def complete(self, id):
        back = request.args.get('back')
        if back:
            back = urllib.unquote(back).encode('utf-8')
        complete_manga_info(manga_id=id)
        return redirect(back) if back else redirect(url_for('manga.MangaLinkView:detail', id=id))

    @route('/edit/<string:id>', methods=['GET', 'POST'])
    def edit(self, id):
        back = request.args.get('back')
        if back:
            back = urllib.unquote(back).encode('utf-8')
        manga_link = MangaLink.objects(id=id).first()
        form = MangaLinkEditForm(obj=manga_link)
        if form.validate_on_submit():
            manga_link.name = form.name.data
            manga_link.author = form.author.data
            manga_link.painter = form.painter.data
            manga_link.desc = form.desc.data
            manga_link.img = form.img.data
            manga_link.save()
            return redirect(back) if back else redirect(url_for('manga.MangaLinkView:detail', id=id))
        else:
            return render_template('links/edit.html', form=form, manga=manga_link)

    @route('/sync/<string:id>', methods=['GET', 'POST'])
    def sync(self, id):
        manga_link = MangaLink.objects(id=id).first()
        manga_info = MangaInfo.objects(original_link=manga_link.link).first()
        if manga_info:
            redirect(url_for('manga.MangaView:detail', id=manga_info.id))
        else:
            manga_info = MangaInfo()
            manga_info.name = manga_link.name
            manga_info.author = manga_link.author
            manga_info.painter = manga_link.painter
            manga_info.desc = manga_link.desc
            manga_info.img = manga_link.img
            manga_info.chapter = len(manga_link.chapters)
            manga_info.original_link = manga_link.link
            manga_info.save()
            parse_all_chapter_to_db(manga_link.link, manga_info.id)
            flash('Success init manga')
            manga_link.sync_flag = True
            manga_link.save()
            return redirect(url_for('manga.ChapterView:index', id=manga_info.id))

@manga.context_processor
def utility_processor():
    def format_date(date):
        return pretty_date(date)

    return dict(format_date=format_date)


MangaView.register(manga)
ChapterView.register(manga)
MangaLinkView.register(manga)
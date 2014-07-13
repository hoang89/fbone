from _ast import keyword
from fbone.manga.forms import AddChapterByHand
from fbone.manga.models import MangaLink, DELETED
from flask import Blueprint, render_template, flash, jsonify, redirect, url_for, request, session
from tools import create_manga
from forms import InsertForm, MangaForm, InitForm, ChapterEditForm, MangaLinkEditForm, MangaEditForm, AddLinkForm
from models import ChapterInfo, MangaInfo
from flask.ext.classy import FlaskView, route
from datetime import datetime
import urllib, requests
from fbone.utils import pretty_date
from html_parse import parse_manga_link, parse_all_manga_from_blog_truyen, parse_all_chapter_from_blog_truyen
from html_parse import complete_manga_info, parse_all_chapter_to_db, add_manga_link
from fbone.decorators import admin_required
from ..category.models import Category
import json

manga = Blueprint('manga', __name__, template_folder='templates')

PER_PAGE = 10

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class MangaView(FlaskView):
    decorators = [admin_required]
    route_base = "manga"

    def index(self):
        page = int(request.args.get('page', 1))
        keyword = request.args.get('keyword', session.get('manga_keyword', None))
        order = request.args.get('order', session.get('manga_order', 'name'))
        status = int(request.args.get('status', session.get('manga_status', '1')))

        if keyword:
            if status != 2:
                items = MangaInfo.objects(name__icontains=keyword, status=status).order_by(('-' + order)).paginate(page=page, per_page=PER_PAGE)
            else:
                items = MangaInfo.objects(name__icontains=keyword).order_by(('-' + order)).paginate(page=page, per_page=PER_PAGE)
        else:
            if status != 2:
                items = MangaInfo.objects(status=status).order_by(('-' + order)).paginate(page=page, per_page=PER_PAGE)
            else:
                items = MangaInfo.objects().order_by(('-' + order)).paginate(page=page, per_page=PER_PAGE)

        session['manga_keyword'] = keyword
        session['manga_order'] = order
        session['manga_status'] = status
        return render_template('manga/index.html', items=items, keyword=keyword, order=order, status=status)

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
        back = request.args.get('back')
        manga_info = MangaInfo.objects(id=id).first()
        form = MangaEditForm(obj=manga_info)
        all = Category.objects().only('name')
        categories = []
        [categories.append(c.name) for c in all]

        if request.method == 'GET':
            pcs = []
            [pcs.append(c.name) for c in manga_info.categories]
            form.clist.data = ",".join(pcs)
            return render_template('manga/edit.html', form=form, id=id, categories=json.dumps(categories), back=back)
        else:
            if manga_info.comment:
                manga_info.history_comment.append(manga_info.comment)
            form.populate_obj(manga_info)
            manga_info.updated_time = datetime.utcnow()

            #remove all category
            for cat in manga_info.categories:
                cat.remove_manga(manga_info)

            ## add manga category:
            clist = form.clist.data.split(',')
            cs = []
            for c in clist:
                category = Category.get_by_name(c.strip())
                if category:
                    category.add_manga(manga_info)
                    cs.append(category)
            manga_info.categories = cs
            manga_info.save()
            return redirect(urllib.unquote(back).decode('utf-8')) if back else redirect(url_for('manga.MangaView:index'))

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

    @route('/delete/<string:id>')
    def delete(self, id):
        back = request.args.get('back')
        manga_info = MangaInfo.objects(id=id).first()
        if manga_info.status != DELETED:
            flash("Cannot deleted this manga, please change status to delete first", 'error')
            return redirect(urllib.unquote(back).decode('utf-8')) if back else redirect(
                url_for('manga.MangaView:index'))

        chapter_info = ChapterInfo.objects(manga=id)
        manga_info.delete()
        chapter_info.delete()
        return redirect(urllib.unquote(back).decode('utf-8')) if back else redirect(
                url_for('manga.MangaView:index'))

    @route("/test/")
    def test(self):
        return render_template("manga/test.html")


class ChapterView(FlaskView):
    decorators = [admin_required]
    route_base = "chapter"

    @route('/<string:id>')
    def index(self, id):
        page = int(request.args.get('page', 1))
        pages = ChapterInfo.objects(manga=id).order_by('-chapter').exclude("links").paginate(page=page, per_page=10)
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

    @route('/add_by_link/<string:id>', methods=['GET', 'POST'])
    def add_by_link(self, id):
        """
        add new chapter from box truyen link
        """
        form = AddLinkForm()
        back = request.args.get('back')
        if form.validate_on_submit():
            link = form.url.data
            add_manga_link(link, manga_id=id)
            return redirect(back) if back else redirect(url_for('manga.ChapterView:index', id=id))
        else:
            return render_template('chapter/add_link.html', form=form, id=id, back=back)


    @route('/add_by_hand/<string:id>', methods=['GET', 'POST'])
    def add_chapter_by_hand(self, id):
        form = AddChapterByHand()
        back = request.args.get('back')
        if form.validate_on_submit():
            return redirect(back) if back else redirect(url_for('manga.ChapterView:index', id=id))
        else:
            return render_template('chapter/add_hand.html', form=form, id=id, back=back)


    @route('/delete/<string:id>')
    def chapter_del(self, id):
        back = request.args.get('back')
        chapter = ChapterInfo.objects(id=id).first()
        chapter.delete()
        flash('Success deleted chapter', 'success')
        return redirect(urllib.unquote(back).decode('utf-8'))

class MangaLinkView(FlaskView):
    decorators = [admin_required]
    route_base = "links"

    @route('/')
    def index(self):
        key_word = session.get('links_key_word', None)
        order = session.get('links_order', 'name')
        key_word = request.args.get('key_word', key_word)
        order = request.args.get('filter', order)
        page = int(request.args.get('page', 1))
        if not key_word:
            paginates = MangaLink.objects().order_by((order)).paginate(page=page, per_page=10)
        else:
            paginates = MangaLink.objects(name__icontains=key_word).order_by((order)).paginate(page=page,
                                                                                                     per_page=10)
        session['links_key_word'] = key_word
        session['links_order'] = order
        return render_template('links/index.html', paginates=paginates, key_word=key_word, filter=order)

    @route('/all/<int:max>')
    def all(self, max):
        """
        Get all managa from bog truyen
        """
        for page in range(1, max):
            all = parse_all_manga_from_blog_truyen(page)

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
        manga_info = MangaInfo.objects(original_link=manga_link.link, status=1).first()
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


@manga.app_template_filter('status')
def status(s):
    if s == 1:
        return u'ACTIVE'
    if s == 0:
        return u'INACTIVE'
    if s == 2:
        return u'DELETED'


MangaView.register(manga)
ChapterView.register(manga)
MangaLinkView.register(manga)
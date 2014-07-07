__author__ = 'hoangnn'

from flask import Blueprint, jsonify, request, abort
from flask.ext.classy import FlaskView, route
from fbone.manga.models import *
import json

manga_api = Blueprint('manga-api', __name__, template_folder='templates')
PER_PAGE = 30
NORMAL = 1
NEW = 2
READ = 3

class MangaApi(FlaskView):
    route_base = 'manga'
    route_prefix = 'api'

    def _to_json(self, list_obj):
        result = []
        map(lambda x: result.append(x.to_manga()), list_obj)
        return result
    def _get_manga(self, page, order):
        pages = MangaInfo.objects(status=ACTIVE).order_by(order).paginate(page=page, per_page=10)
        mangas = pages.items
        res = {'data': self._to_json(mangas), 'has_next': pages.has_next, 'page': pages.page}
        return jsonify(res)

    def index(self):
        try:
            page = int(request.args.get('page', 1))
        except:
            page = 1

        try:
            type = int(request.args.get('type', 1))
        except:
            type=1

        if type == NORMAL:
            return self._get_manga(page=page, order='name')

        if type == NEW:
            return self._top_new(page=page)

        if type == READ:
            return self._top_read(page=page)
        else:
            abort(404)

    def _top_read(self, page):
        return self._get_manga(page=page, order='-read_count')

    def _top_new(self, page):
        return self._get_manga(page=page, order='-modified_at')

class ChapterApi(FlaskView):
    route_base = 'chapter'
    route_prefix = 'api'

    def _to_json(self, list_obj):
        result = []
        map(lambda x: result.append(x.to_chapter()), list_obj)
        return result

    @route('/<string:id>')
    def index(self, id):
        try:
            page = int(request.args.get('page', 1))
        except:
            page = 1

        pages = ChapterInfo.objects(status=ACTIVE, manga=id).order_by('-chapter').paginate(page=page, per_page=PER_PAGE)
        chapters = pages.items
        res = {'data': self._to_json(chapters), 'has_next': pages.has_next, 'page': pages.page}
        return jsonify(res)

    @route('/list/<string:id>')
    def list(self, id):
        try:
            current = int(request.args.get('c', 0))
        except:
            current = 0
        chapters = ChapterInfo.objects(chapter__gt=current, manga=id).order_by('-chapter')
        res={'data': self._to_json(chapters)}
        return jsonify(res)

    @route('/detail/<string:id>')
    def detail(self, id):
        chapter = ChapterInfo.objects(id=id).first()
        return jsonify(chapter.detail_json())


MangaApi.register(manga_api)
ChapterApi.register(manga_api)

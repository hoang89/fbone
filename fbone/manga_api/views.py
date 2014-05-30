__author__ = 'hoangnn'

from flask import Blueprint, jsonify, request
from flask.ext.classy import FlaskView, route
from fbone.manga.models import *

manga_api = Blueprint('manga-api', __name__, template_folder='templates')


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
        return self._get_manga(page=page, order='name')

    @route('/top/read')
    def top_read(self):
        try:
            page = int(request.args.get('page', 1))
        except:
            page = 1
        return self._get_manga(page=page, order='-read_count')

    @route('/top/new')
    def top_new(self):
        try:
            page = int(request.args.get('page', 1))
        except:
            page = 1
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

        pages = ChapterInfo.objects(status=ACTIVE, manga=id).order_by('created_at').paginate(page=page, per_page=10)
        chapters = pages.items
        res = {'data': self._to_json(chapters), 'has_next': pages.has_next, 'page': pages.page}
        return jsonify(res)


MangaApi.register(manga_api)
ChapterApi.register(manga_api)
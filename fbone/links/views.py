from fbone.links.forms import ChapterLinkForm

__author__ = 'hoangnn'
from flask.ext.classy import FlaskView, route
from flask import request, redirect, render_template, Blueprint
from html_parse import get_chapter_file_link

links = Blueprint("links", __name__, template_folder="templates")

class LinksView(FlaskView):
    route_base = "leaks"

    def index(self):
        return "Ok"

    @route('/gbchapter/', methods=["GET","POST"])
    def get_chapter_blog(self):
        form = ChapterLinkForm()
        if form.validate_on_submit():
            result = get_chapter_file_link(form.link.data)
            return render_template("links/chapter_preview.html", result=result)
        else:
            return render_template("links/blog_chapter.html", form=form)


LinksView.register(links)
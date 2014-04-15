__author__ = 'hoangnn'
from flask import Blueprint, request, render_template
from .services import ContentService

content = Blueprint("content", __name__, template_folder="templates", url_prefix="/content")

@content.route("/", methods=["GET", "POST"])
def index():
    link = request.args["link"]
    if link is None:
        link = "http://m.dantri.com.vn/"
    html = ContentService.parse_link(link)
    #return render_template("index.html", content=html)
    return html

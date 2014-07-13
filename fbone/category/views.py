__author__ = 'hoangnn'

from flask import Blueprint, render_template, redirect, request, abort, flash, url_for
from models import Category
from forms import CategoryForm
from flask.ext.classy import FlaskView, route

category  = Blueprint('category', __name__,template_folder='templates')

class CategoryView(FlaskView):
    route_prefix = "mc"
    route_base = "/"

    def index(self):
        form = CategoryForm()
        categories = Category.objects()
        return render_template('category/index.html', categories=categories, form=form)

    @route('/add', methods=["GET","POST"])
    def add(self):
        form = CategoryForm()
        if form.validate_on_submit():
            category = Category()
            category.name = form.name.data
            category.slug = form.slug.data
            category.save()
            flash('Success add category', 'success')
            return redirect(url_for('category.CategoryView:index'))
        else:
            abort(403)

class TopCategoryView(FlaskView):
    route_base = "/"
    route_prefix = "category"

    route('/<string:slug>')
    def index(self, slug):
        category = Category.objects(slug=slug).first()
        if not category:
            return abort(404)
        return render_template('ctop/index.html', mangas=category.mangas)



CategoryView.register(category)
TopCategoryView.register(category)

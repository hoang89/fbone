__author__ = 'hoangnn'

from flask import Blueprint, render_template, redirect, request, abort, flash, url_for
from models import MCategory
from forms import CategoryForm

mcategory  = Blueprint('mcategory', __name__, url_prefix='/mca', template_folder='templates')
#MCategoryForm = model_form(MCategory)

@mcategory.route('/')
def index():
    form = CategoryForm()
    categories = MCategory.objects()
    return render_template('category/index.html', categories=categories, form=form)

@mcategory.route('/insert', methods=['POST','GET'])
def insert():
    form = CategoryForm()
    if form.validate_on_submit():
        mcategory = MCategory()
        mcategory.name = form.name.data
        mcategory.language = form.language.data
        mcategory.save()
        flash('Success add category', 'success')
        return redirect(url_for('mcategory.index'))
    else:
        abort(403)
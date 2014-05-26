__author__ = 'hoangnn'

from flask.ext.wtf import Form, StringField, IntegerField, Required, SubmitField

class CategoryForm(Form):
    name = StringField()
    language = StringField()
    submit = SubmitField(u'Add Category')
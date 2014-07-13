__author__ = 'hoangnn'

from flask.ext.wtf import Form, StringField, IntegerField, Required, SubmitField

class CategoryForm(Form):
    name = StringField(validators=[Required()])
    slug = StringField(validators=[Required()])
    submit = SubmitField(u'Add Category')
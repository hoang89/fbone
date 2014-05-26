__author__ = 'hoangnn'

from flask.ext.wtf import Form, StringField, IntegerField, Required, SubmitField, TextAreaField

class InsertForm(Form):
    chapter = IntegerField(validators=[Required()])
    base = StringField(validators=[Required()])
    max = IntegerField(validators=[Required()])
    submit = SubmitField(u'Add manga chapter')

class MangaForm(Form):
    name = StringField(validators=[Required()])
    author = StringField(validators=[Required()])
    painter = StringField()
    language = StringField()
    desc = TextAreaField()
    img = StringField()
    submit = SubmitField(u'Add manga')
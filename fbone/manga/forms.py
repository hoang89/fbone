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

class InitForm(Form):
    url = StringField(validators=[Required()])
    submit = SubmitField(u'Init Manga')

class ChapterEditForm(Form):
    name = StringField(validators=[Required()])
    chapter = StringField(validators=[Required()])
    page = IntegerField(validators=[Required()])
    avatar = StringField(validators=[Required()])
    submit = SubmitField(u'Edit chapter')
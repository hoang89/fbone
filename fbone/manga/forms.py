__author__ = 'hoangnn'

from flask.ext.wtf import Form, StringField, IntegerField, Required, SubmitField, TextAreaField, SelectField

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

class MangaEditForm(Form):
    name = StringField(validators=[Required()])
    status = SelectField(u'Status', choices=[('1', 'Active'),('0', 'Inactive'),('2', 'Delete')])
    author = StringField(validators=[Required()])
    painter = StringField()
    language = StringField()
    desc = TextAreaField()
    img = StringField()
    comment = TextAreaField()
    submit = SubmitField(u'Edit manga')

class InitForm(Form):
    url = StringField(validators=[Required()])
    submit = SubmitField(u'Init Manga')

class ChapterEditForm(Form):
    name = StringField(validators=[Required()])
    chapter = StringField(validators=[Required()])
    page = IntegerField(validators=[Required()])
    avatar = StringField(validators=[Required()])
    chapter_status = SelectField(choices=[('1', 'Active'), ('0', 'Inactive'), ('3', 'Delete')])
    submit = SubmitField(u'Edit chapter')

class MangaLinkEditForm(Form):
    name = StringField()
    desc = TextAreaField()
    author = StringField()
    painter = StringField()
    img = StringField()
    submit = SubmitField(u'Edit link')

class AddLinkForm(Form):
    url = StringField(validators=[Required()])
    submit = SubmitField(u'Add Manga Chapter')

class AddChapterByHand(Form):
    name = StringField("Chapter Name", validators=[Required()])
    chapter = StringField("Chapter number", validators=[Required()])
    avatar = StringField("Avatar image", validators=[Required()])
    page = StringField("Page number")
    links = TextAreaField("Image links")
    submit = SubmitField(u'Add Manga Chapter')

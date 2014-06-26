__author__ = 'hoangnn'

from flask.ext.wtf import Form, StringField, IntegerField, Required, SubmitField, TextAreaField, SelectField

class ChapterLinkForm(Form):
    link = StringField("Chapter Link")
    submit = SubmitField("Get Chapter Info")
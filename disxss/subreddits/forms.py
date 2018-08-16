# -*- coding: utf-8 -*-
"""
"""


from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField
from wtforms.validators import Required, URL, Length

from disxss.threads import constants as THREAD

class SubmitForm(FlaskForm):
    name = TextField('Name your community!', [Required()])
    desc = TextAreaField('Description of subreddit!', [Required()])

# -*- coding: utf-8 -*-
"""
"""
from flask import (Blueprint, request, render_template, flash, g, session,
    redirect, url_for, abort)
from bson import ObjectId

# TODO: frontends, db imports
# # from flask_reddit import db
from disxss.frontends.views import get_subreddits

from disxss.users.models import User

from disxss.users.decorators import requires_login
from disxss import app
from disxss import db

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        g.user = db.users.find({'_id': ObjectId(session['user_id'])})
        app.logger.debug("filter user : {}".format(session['user_id']))


@bp.route('/<username>/')
def home_page(username=None):
    if not username:
        abort(404)

    # TODO: port to mongodb query
    # user = User.query.filter_by(username=username).first()
    # user = db.users.find({'username': username}).username#.first()
    user = db.users.find_one_or_404({"username": username})
    if not user:
        abort(404)
    return render_template('users/profile.html', user=g.user, current_user=user,
            subreddits = get_subreddits())

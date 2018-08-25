# -*- coding: utf-8 -*-
"""
"""
from flask import (Blueprint, request, render_template, flash, g, session,
    redirect, url_for, abort, jsonify)
from bson import ObjectId

# TODO: frontends, db imports
# # from flask_reddit import db
from disxss.frontends.views import get_subreddits

from disxss.users.models import User, dump_user_no_pass
from disxss.threads.models import Thread
from disxss.users.decorators import requires_login
from disxss import app
from disxss import db

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        g.user = db.users.find({'_id': ObjectId(session['user_id'])})[0]
        app.logger.debug("filter user : {}".format(session['user_id']))


@bp.route('/<username>/')
def home_page(username=None):
    if not username:
        abort(404)

    # TODO: port to mongodb query
    # user = User.query.filter_by(username=username).first()
    cursor = User.find({'username': username})
    user = cursor[0]
    # user['thread_karma'] = Thread.find({"user_id":user.id})
    app.logger.debug("user cursor: {}".format(cursor))
    app.logger.debug("user dict: {}".format(user))
    app.logger.debug("thread karma: {}".format(user.get_thread_karma()))
    # user = db.users.find_one_or_404({"username": username})

    # threads = Thread.find({'user_id': user.id})
    if not user:
        abort(404)
    return render_template('users/profile.html',
            user=user, current_user=user,
            subreddits = get_subreddits(),
            )



@app.route('/users', methods=['GET'])
def list_users():
    page = int(request.args.get('page', 1))
    users = User.find().limit(10).skip((page - 1) * 10)
    return jsonify({
        '_total': users.count(),
        '_page': page,
        '_per_page': 10,
        '_items': [dump_user_no_pass(u) for u in users]
    })

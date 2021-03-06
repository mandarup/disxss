# -*- coding: utf-8 -*-
"""
All view code for async get/post calls towards the server
must be contained in this file.
"""
from flask import (Blueprint, request, render_template, flash, g,
        session, redirect, url_for, jsonify, abort)
from werkzeug import check_password_hash, generate_password_hash
from bson import json_util, ObjectId

# from flask_reddit import db
from disxss.users.models import User
from disxss.threads.models import Thread, Comment
from disxss.users.decorators import requires_login
from disxss import app

bp = Blueprint('apis', __name__, url_prefix='/apis')


@bp.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.find_one({'id': ObjectId(session['user_id'])})
        app.logger.debug("filter user apis : {}".format(session['user_id']))


@bp.route('/comments/submit/', methods=['POST'])
@requires_login
def submit_comment():
    """
    Submit comments via ajax
    """
    thread_id = request.form['thread_id']
    comment_text = request.form['comment_text']
    comment_parent_id = request.form['parent_id'] # empty means none

    app.logger.debug("thread_id: {}".format(thread_id))
    app.logger.debug("comment_text: {}".format(comment_text))
    app.logger.debug("comment_parent_id: {}".format(comment_parent_id))
    app.logger.debug("in apis.views.submit_comment")

    if not comment_text:
        abort(404)

    for thread in Thread.find():
        app.logger.debug(thread)
    app.logger.debug("num threads: {}".format(Thread.find().count()))
    thread = Thread.find_one({"id": ObjectId(thread_id)})
    app.logger.debug(thread)
    # app.logger.debug(list(thread))
    comment = thread.add_comment(comment_text, comment_parent_id,
            g.user.id)

    user_has_voted = comment.has_voted(g.user.id)
    num_votes = comment.num_votes

    return jsonify(comment_text=comment.text, date=comment.pretty_date(),
            username=g.user.username, comment_id=str(comment.id),
            margin_left=comment.get_margin_left(),
            user_has_voted=user_has_voted,
            num_votes=num_votes)

@bp.route('/threads/vote/', methods=['POST'])
@requires_login
def vote_thread():
    """
    Submit votes via ajax
    """
    thread_id = ObjectId(request.form['thread_id'])
    user_id = g.user.id
    app.logger.debug("thread_id: {}".format(thread_id))

    if not thread_id:
        abort(404)

    thread = Thread.find_one({"id": thread_id})
    vote_status = thread.vote(user_id=user_id)
    app.logger.debug(thread)
    app.logger.debug("vote_status: {}".format(vote_status))

    return jsonify(new_votes=thread.num_votes, vote_status=vote_status)

@bp.route('/comments/vote/', methods=['POST'])
@requires_login
def vote_comment():
    """
    Submit votes via ajax
    """
    comment_id = request.form['comment_id']
    user_id = g.user.id

    if not comment_id:
        abort(404)

    comment = Comment.find_one({"id": ObjectId(comment_id)})
    vote_status = comment.vote(user_id=user_id)
    return jsonify(new_votes=comment.num_votes, vote_status=vote_status)

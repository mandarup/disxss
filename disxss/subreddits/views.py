# -*- coding: utf-8 -*-
"""
"""
from flask import (Blueprint, request, render_template, flash, g,
        session, redirect, url_for, abort)
from bson import ObjectId

from disxss.frontends.views import get_subreddits, process_thread_paginator
from disxss.subreddits.forms import SubmitForm
from disxss.subreddits.models import Subreddit
from disxss.threads.models import Thread
from disxss.users.models import User
from disxss import db
from disxss import app

bp = Blueprint('subreddits', __name__, url_prefix='/r')

#######################
### Subreddit Views ###
#######################

@bp.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.find({'id': ObjectId(session['user_id'])})[0]
        app.logger.debug("filter user : {}".format(session['user_id']))


def meets_subreddit_criterea(subreddit):
    return True

@bp.route('/subreddits/submit/', methods=['GET', 'POST'])
def submit():
    """
    """
    if g.user is None:
        flash('You must be logged in to submit subreddits!', 'danger')
        return redirect(url_for('frontends.login', next=request.path))

    form = SubmitForm(request.form)
    app.logger.debug(g.user)
    user_id = g.user.id

    if form.validate_on_submit():
        name = form.name.data.strip()
        desc = form.desc.data.strip()

        subreddit = Subreddit.find_one({'name':name})
        if subreddit:
            flash('subreddit already exists!', 'danger')
            return render_template('subreddits/submit.html', form=form, user=g.user,
                subreddits=get_subreddits())

        _new_subreddit = {"name":name, "desc":desc, "admin_id":user_id,
                            "admin": g.user}
        new_subreddit = Subreddit(**_new_subreddit)
        new_subreddit.commit()

        if not meets_subreddit_criterea(subreddit):
            return render_template('subreddits/submit.html', form=form, user=g.user,
                subreddits=get_subreddits())

        # db.session.add(new_subreddit)
        # db.session.commit()

        flash('Thanks for starting a community! Begin adding posts to your community\
                by clicking the red button to the right.', 'success')
        return redirect(url_for('subreddits.permalink', subreddit_name=new_subreddit.name))
    return render_template('subreddits/submit.html', form=form, user=g.user,
            subreddits=get_subreddits())

@bp.route('/delete/', methods=['GET', 'POST'])
def delete():
    """
    """
    pass

@bp.route('/subreddits/view_all/', methods=['GET'])
def view_all():
    """
    """
    return render_template('subreddits/all.html', user=g.user,
            subreddits=Subreddit.find())

@bp.route('/<subreddit_name>/', methods=['GET'])
def permalink(subreddit_name=""):
    """
    """
    subreddit = Subreddit.find_one({"name":subreddit_name})
    app.logger.debug("subreddit: {}".format(subreddit))
    if not subreddit:
        abort(404)

    trending = True if request.args.get('trending') else False
    thread_paginator = process_thread_paginator(trending=trending, subreddit=subreddit)
    subreddits = get_subreddits()

    return render_template('home.html', user=g.user, thread_paginator=thread_paginator,
        subreddits=subreddits, cur_subreddit=subreddit)

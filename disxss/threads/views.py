# -*- coding: utf-8 -*-
"""
"""


from bson.objectid import ObjectId

from flask import (Blueprint, request, render_template, flash, g, session,
    redirect, url_for, abort)


from disxss.threads.forms import SubmitForm
from disxss.threads.models import Thread
from disxss.users.models import User
from disxss.subreddits.models import Subreddit
from disxss.frontends.views import get_subreddits
from disxss import db
from disxss import app

bp = Blueprint('threads', __name__, url_prefix='/threads')

# Threads Views #

@bp.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.find({'id': ObjectId(session['user_id'])})[0]
        app.logger.debug("filter user : {}".format(session['user_id']))


def meets_thread_criteria(thread):
    """
    """
    app.logger.debug("thread: {}".format(thread))
    if not thread.title:
        flash('You must include a title!', 'danger')
        return False
    if not thread.text and not thread.link:
        flash('You must post either body text or a link!', 'danger')
        return False

    dup_link = Thread.find_one({"link":thread.link})
    if not thread.text and dup_link:
        flash('someone has already posted the same link as you!', 'danger')
        return False

    return True

@bp.route('/<subreddit_name>/submit/', methods=['GET', 'POST'])
def submit(subreddit_name=None):
    """
    """
    if g.user is None:
        flash('You must be logged in to submit posts!', 'danger')
        return redirect(url_for('frontends.login', next=request.path))
    user_id = g.user.id


    subreddits = Subreddit.find({"name":subreddit_name})
    subreddit = None
    if subreddits.count() > 0:
        subreddit = subreddits[0]
    if not subreddit:
        flash('Select a subreddit!', 'danger')
        # abort(404)
        return redirect(url_for('frontends.home', next=request.path))


    form = SubmitForm(request.form)
    if form.validate_on_submit():
        title = form.title.data.strip()
        link = form.link.data.strip()
        text = form.text.data.strip()

        thread_data = {"title":title, "link":link, "text":text,
                "user_id":user_id, "subreddit_id":subreddit.id}
        thread = Thread(**thread_data)

        if not meets_thread_criteria(thread):
            return render_template('threads/submit.html', form=form, user=g.user,
                cur_subreddit=subreddit.name)

        thread.update()
        thread.commit()
        # db.threads.add_thread
        # db.session.add(thread)
        # db.session.commit()

        # thread.set_hotness()
        # thread.add_thread()

        flash('thanks for submitting!', 'success')
        return redirect(url_for('subreddits.permalink', subreddit_name=subreddit.name))
    return render_template('threads/submit.html', form=form, user=g.user,
            cur_subreddit=subreddit, subreddits=get_subreddits())

@bp.route('/delete/', methods=['GET', 'POST'])
def delete():
    """
    """
    pass

@bp.route('/edit/', methods=['GET', 'POST'])
def edit():
    """
    """
    pass

@bp.route('/<subreddit_name>/<thread_id>/<path:title>/', methods=['GET', 'POST'])
def thread_permalink(subreddit_name=None, thread_id=None, title=None):
    """
    """
    thread_id = thread_id #or -99
    thread = Thread.find_one_or_404({"id": ObjectId(thread_id)})
    subreddit = Subreddit.find_one(name=subreddit_name)
    subreddits = get_subreddits()
    return render_template('threads/permalink.html', user=g.user, thread=thread,
            cur_subreddit=subreddit, subreddits=subreddits)


##########################
##### Comments Views #####
##########################

@bp.route('/comments/submit/', methods=['GET', 'POST'])
def submit_comment():
    """
    """
    pass

@bp.route('/comments/delete/', methods=['GET', 'POST'])
def delete_comment():
    """
    """
    pass

@bp.route('/comments/<comment_id>/', methods=['GET', 'POST'])
def comment_permalink():
    """
    """
    pass

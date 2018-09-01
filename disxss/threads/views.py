# -*- coding: utf-8 -*-
"""
"""


from bson.objectid import ObjectId

from flask import (Blueprint, request, render_template, flash, g, session,
    redirect, url_for, abort)


from disxss.threads.forms import SubmitForm
from disxss.threads.models import Thread
from disxss.users.models import User
from disxss.categories.models import Category
from disxss.frontends.views import get_categories
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
    app.logger.debug("duplicate link: {}".format(dup_link))
    if not thread.text or dup_link:
        flash('someone has already posted the same link as you!', 'danger')
        return False

    return True

@bp.route('/<category_name>/submit/', methods=['GET', 'POST'])
def submit(category_name=None):
    """
    """
    if g.user is None:
        flash('You must be logged in to submit posts!', 'danger')
        return redirect(url_for('frontends.login', next=request.path))
    user_id = g.user.id


    categories = Category.find({"name":category_name})
    category = None
    if categories.count() > 0:
        category = categories[0]
    if not category:
        flash('Select a category!', 'danger')
        # abort(404)
        return redirect(url_for('frontends.home', next=request.path))


    form = SubmitForm(request.form)
    if form.validate_on_submit():
        title = form.title.data.strip()
        link = form.link.data.strip()
        text = form.text.data.strip()

        thread_data = {"title":title, "link":link, "text":text,
                "user_id":user_id, "category_id":category.id,
                "user": g.user,
                "category": category}
        thread = Thread(**thread_data)

        if not meets_thread_criteria(thread):
            return render_template('threads/submit.html', form=form, user=g.user,
                cur_category=category.name)

        thread.update()
        thread.commit()
        app.logger.debug("adding thread: category name: {}"
                         .format(thread.category))
        app.logger.debug("adding thread: category name: {}"
                         .format(thread.category.fetch().name))
        # db.threads.add_thread
        # db.session.add(thread)
        # db.session.commit()

        # thread.set_hotness()
        # thread.add_thread()

        flash('thanks for submitting!', 'success')
        return redirect(url_for('categories.permalink', category_name=category.name))
    return render_template('threads/submit.html', form=form, user=g.user,
            cur_category=category, categories=get_categories())

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

@bp.route('/<category_name>/<thread_id>/<path:title>/', methods=['GET', 'POST'])
def thread_permalink(category_name=None, thread_id=None, title=None):
    """
    """
    thread_id = thread_id #or -99
    app.logger.debug("thread_id: {}".format(thread_id))
    thread = Thread.find_one({"id": ObjectId(thread_id)})

    app.logger.debug(Category.find({"name":category_name}))
    category = Category.find_one({"name":category_name})
    categories = get_categories()
    return render_template('threads/permalink.html', user=g.user, thread=thread,
            cur_category=category, categories=categories)


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

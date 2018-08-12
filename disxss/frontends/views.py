# -*- coding: utf-8 -*-
"""
"""

import flask
from flask import (Blueprint, request, render_template, flash,
    g, session, redirect, url_for, jsonify, abort)

from werkzeug import check_password_hash, generate_password_hash
import datetime
from easydict import EasyDict as edict
from bson import json_util, ObjectId
import pymongo
from umongo import ValidationError

# from disxss import db
from disxss.users.forms import RegisterForm, LoginForm
from disxss.users.models import User
from disxss.users.decorators import requires_login
from disxss import app
from disxss.threads.models import Thread
from disxss.subreddits.models import Subreddit
from disxss import search_utils # don't override function name

from disxss import db
from disxss import db_utils


bp = Blueprint('frontends', __name__, url_prefix='')

@bp.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        app.logger.debug({'id': session['user_id']})
        g.user = User.find({'id': ObjectId(session['user_id'])})[0]
        # g.user = User.query.get(session['user_id'])
        # g.user = User(document=users.find_one_or_404({'_id': ObjectId(session['user_id'])}))

def home_subreddit():

    #TODO: convert to mongodb
    # return Subreddit.query.get_or_404(1)

    s = Subreddit.find_one({})
    # if s is None:
    #     abort(404)
    return s

def get_subreddits():
    """
    important and widely imported method because a list of
    the top 30 subreddits are present on every page in the sidebar
    """

    # TODO:
    # convert to mongodb
    # subreddits = []
    # subreddits = Subreddit.query.filter(Subreddit.id != 1)[:25]
    subreddits = Subreddit.find({"id": {"$ne": 1}})[:25]
    app.logger.debug("in frontends.views: subreddits: {}".format(subreddits))
    return subreddits

def process_thread_paginator(trending=False, rs=None, subreddit=None):
    """
    abstracted because many sources pull from a thread listing
    source (subreddit permalink, homepage, etc)
    """
    threads_per_page = 15
    cur_page = request.args.get('page') or 1
    cur_page = int(cur_page)
    thread_paginator = None

    # if we are passing in a resultset, that means we are just looking to
    # quickly paginate some arbitrary data, no sorting
    if rs:
        # thread_paginator = rs.paginate(cur_page, per_page=threads_per_page,
        #     error_out=True)
        thread_paginator=db_utils.paginate(rs, page_num=cur_page, page_size=threads_per_page)
        return thread_paginator

    # sexy line of code :)
    app.logger.debug("subreddit: {}".format(subreddit))
    app.logger.debug("Thread: {}".format(Thread.find()))
    def get_base_query():
        if subreddit is not None and subreddit.threads is not None:
            app.logger.debug("subreddit.threads: {}".format(subreddit.threads))
            return subreddit.threads.find()
        else:
            return Thread.find()

    base_query = get_base_query()

    if trending:
        thread_paginator = base_query.sort([("votes", pymongo.DESCENDING)])
        thread_paginator = db_utils.paginate(thread_paginator, page_num=cur_page, page_size=threads_per_page)
    else:
        thread_paginator = base_query.sort([("hotness", pymongo.DESCENDING)])
        thread_paginator = db_utils.paginate(thread_paginator, page_num=cur_page, page_size=threads_per_page)
    return thread_paginator

#@bp.route('/<regex("trending"):trending>/')
@bp.route('/')
def home(trending=False):
    """
    If not trending we order by creation date
    """
    trending = True if request.args.get('trending') else False
    subreddits = get_subreddits()


    #---------------------------------------------------------------------
    # TODO: fix pagination
    thread_paginator = process_thread_paginator(trending)
    # thread_paginator = []
    #---------------------------------------------------------------------


    return render_template('home.html', user=g.user,
            subreddits=subreddits,
            cur_subreddit=home_subreddit(),
            thread_paginator=thread_paginator)

@bp.route('/search/', methods=['GET'])
def search():
    """
    Allows users to search threads and comments
    """
    query = request.args.get('query')
    rs = search_utils.search(query, orderby='date_created', search_title=True,
            search_text=True, limit=100)

    thread_paginator = process_thread_paginator(rs=rs)
    # rs = rs.find()
    num_searches = rs.count()
    subreddits = get_subreddits()

    return render_template('home.html', user=g.user,
            subreddits=subreddits, cur_subreddit=home_subreddit(),
            thread_paginator=thread_paginator, num_searches=num_searches)

@bp.route('/login/', methods=['GET', 'POST'])
def login():
    """
    We had to do some extra work to route the user back to
    his or her original place before logging in
    """
    if g.user:
        return redirect(url_for('frontends.home'))

    next = ''
    if request.method == 'GET':
        if 'next' in request.args:
            next = request.args['next']

    form = LoginForm(request.form)
    # make sure data is valid, but doesn't validate password is right
    if form.validate_on_submit():
        # continue where we left off if so
        # user = User.query.filter_by(email=form.email.data).first()

        # app.logger.debug(db.users.find({'email': form.email.data})[0])
        app.logger.debug({'email': form.email.data})

        app.logger.debug(User.find({'email': form.email.data}))
        user = User.find({'email': form.email.data})[0]
        app.logger.debug("user: {user}".format(user=user))
        app.logger.debug("finding email: {}".format(form.email.data))
        app.logger.debug("user found: {}".format((user.email, user.username)))
        # user = edict(user)

        # user = User(document=document)

        # we use werzeug to validate user's password
        if user and check_password_hash(user.password, form.password.data):
            # the session can't be modified as it's signed,
            # it's a safe place to store the user id
            app.logger.debug("user: {}".format(user.username))

            session['user_id'] = str(user.id)

            if 'next' in request.form and request.form['next']:
                return redirect(request.form['next'])

            flash('You are logged in', 'success')
            return redirect(url_for('frontends.home'))

        elif not user:
            flash("You haven't signed up, please register", 'danger')
            return redirect(url_for('frontends.register'))
        else:
            flash('Wrong email or password', 'danger')
    return render_template("login.html", form=form, next=next)

@bp.route('/logout/', methods=['GET', 'POST'])
@requires_login
def logout():
    session.pop('user_id', None)
    return redirect(url_for('frontends.home'))

@bp.route('/register/', methods=['GET', 'POST'])
def register():
    """
    """

    app.logger.debug("request.args: {}".format(request.args))
    next = ''
    if request.method == 'GET':
        if 'next' in request.args:
            next = request.args['next']

    form = RegisterForm(request.form)
    app.logger.debug("form: {}"
        .format("\n".join("-- form -- {}: {}".format(k,v) for k,v in form.__dict__.items())))


    app.logger.debug("is submitted: {}".format(form.is_submitted()))
    app.logger.debug("is validated: {}".format(form.validate()))

    if form.validate_on_submit():
        # create an user instance not yet stored in the database
        created_at = datetime.datetime.now()
        modified_at = datetime.datetime.now()

        app.logger.debug("username : {}".format(form.username))
        app.logger.debug("password : {}".format(form._fields['password'].data))
        app.logger.debug("password : {}".format(form.password.data))
        app.logger.debug("username : {}".format(form.username.data))

        app.logger.debug("username : {}".format(generate_password_hash(form.password.data)))

        # user = User(username=form.username.data, email=form.email.data,
        #         password=generate_password_hash(form.password.data),
        #         # created_at=created_at,
        #         # modified_at=modified_at
        #         )

        password = generate_password_hash(form.password.data)
        # user = User(username=form.username.data,
        #             email=form.email.data,
        #         password=password,
        #         created_at=created_at,
        #         modified_at=modified_at
        #         ).save()

        data = {'username':form.username.data,
                'email':form.email.data,
                'password':password,
                # 'created_at':created_at,
                # 'modified_at':modified_at
                }

        # user = User(**userdoc).save()
        User.ensure_indexes()

        try:
            user = User(**data)
            user.commit()
        except ValidationError as e:
            app.logger.error(str(e))
            flash(str(e), 'danger')
            return redirect(url_for('frontends.register'))

        # User(**data).commit()
        # user = User.find_one({'email': data['email']})

        # user_id = db.users.insert_one(post).inserted_id

        # Insert the record in our database and commit it
        # db.session.add(user)
        # db.session.commit()
        # user.save()

        # Log the user in, as he now has an id
        app.logger.debug("username: {}".format(user.username))
        # session['user_id'] = json_util.dumps({"user_id":user.id})["user_id"]
        session["user_id"] = str(user.id)
        app.logger.debug("user_id: {}".format(session['user_id']))

        app.logger.debug("csrf_token: {}".format(form.csrf_token.data))
        session['csrf_token'] = form.csrf_token.data

        flash('thanks for signing up!', 'success')
        if 'next' in request.form and request.form['next']:
            return redirect(request.form['next'])
        return redirect(url_for('frontends.home'))


    return render_template("register.html", form=form, next=next)

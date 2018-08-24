# -*- coding: utf-8 -*-
"""
All database abstractions for threads and comments
go in this file.

"""

import math
import datetime


from bson.objectid import ObjectId
import pymongo

from umongo import Instance, Document, fields, ValidationError, set_gettext
from umongo import validate
from umongo import EmbeddedDocument
from umongo.marshmallow_bonus import SchemaFromUmongo

from disxss import db
from disxss.threads import constants as THREAD
from disxss import utils
from disxss import media
from disxss import instance
from disxss.users import models as user_model
from disxss.subreddits import models as subreddits_model
from disxss import app

# thread_upvotes = db.Table('thread_upvotes',
#     db.Column('user_id', db.Integer, db.ForeignKey('users_user.id')),
#     db.Column('thread_id', db.Integer, db.ForeignKey('threads_thread.id'))
# )
#
# comment_upvotes = db.Table('comment_upvotes',
#     db.Column('user_id', db.Integer, db.ForeignKey('users_user.id')),
#     db.Column('comment_id', db.Integer, db.ForeignKey('threads_comment.id'))
# )
#

thread_upvotes = db.thread_upvotes
comment_upvotes = db.comment_upvotes


@instance.register
class ThreadUpvote(Document):
    user_id = fields.ReferenceField("User") # Integer?
    thread_id = fields.ReferenceField("Thread") # Integer?

    class Meta:
        collection_name = "thread_upvotes"


@instance.register
class CommentUpvote(Document):
    user_id = fields.ReferenceField("User") # Integer?
    comment_id = fields.ReferenceField("Comment") # Integer?

    class Meta:
        collection_name = "comment_upvotes"


@instance.register
class Thread(Document):
    """
    We will mimic reddit, with votable threads. Each thread may have either
    a body text or a link, but not both.
    """
    # __tablename__ = 'threads_thread'

    title = fields.StrField(validate=validate.Length(max=THREAD.MAX_TITLE),
                            default=None) # b.StringField(THREAD.MAX_TITLE)

    text = fields.StrField( default=None,
                            validate=validate.Length(max=THREAD.MAX_BODY))
    link = fields.StrField(default=None,
                           validate=validate.Length(max=THREAD.MAX_LINK))
    thumbnail = fields.StrField( default=None,
                                 validate=validate.Length(max=THREAD.MAX_LINK))

    # NOTE: this should be ReferenceField
    user_id = fields.ObjectIdField() # Integer?
    subreddit_id = fields.ObjectIdField() #

    user = fields.ReferenceField("User") # Integer?
    subreddit = fields.ReferenceField("Subreddit")

    comment_ids = fields.ListField(fields.ObjectIdField())
    comments = fields.ListField(fields.ReferenceField("Comment"))

    date_created = fields.DateTimeField(
        default=datetime.datetime.now(),
        missing=datetime.datetime.now())
    date_modified = fields.DateTimeField(
        default=datetime.datetime.now(),
        missing=datetime.datetime.now(),)

    status = fields.IntegerField(default=THREAD.ALIVE)

    num_votes = fields.IntegerField(default=0, missing=0)
    hotness = fields.IntegerField(default=0, missing=0)

    def update(self):
        if not self.date_created:
            self.date_created = datetime.datetime.now()
        self.date_modified = datetime.datetime.now()
        # self.subreddit = self.get_subreddit()
        # self.user = self.get_user()
        self.set_hotness()
        self.extract_thumbnail()
        return self

    class Meta:
        # collection = db.threads
        collection_name = "threads"
        indexes = ('username', '$text', 'title')


    # def get_subreddit(self):
    #     return subreddits_model.Subreddit.find({"id": self.subreddit_id})[0]

    # def get_user(self):
    #     return user_model.User.find({"id": self.user_id})[0]


    # def __init__(self, title, text, link, user_id, subreddit_id):
    #     self.title = title
    #     self.text = text
    #     self.link = link
    #     self.user_id = user_id
    #     self.subreddit_id = subreddit_id
    #     self.extract_thumbnail()
    #
    #     self.created_on = datetime.datetime.utcnow()
    #     self.updated_on = datetime.datetime.utcnow()
    #
    #     self.upvotes = 0
    #
    #     self.set_hotness()
    #     self.add_thread()
    #
    #
    # def get_thread(self):
    #     thread = {"title": self.title,
    #               "text" : self.text,
    #               "link": self.link,
    #               "user_id": self.user_id,
    #               "subreddit_id": self.subreddit_id,
    #               "created_on": self.created_on,
    #               "updated_on": self.updated_on,
    #               "upvotes": self.upvotes,
    #               "hotness": self.hotness}
    #     return thread
    #
    # def add_thread(self):
    #     thread = self.get_thread()
    #     id = db.threads.insert_one(thread).inserted_id
    #     self.set_id(id)
    #     return self
    #
    # def set_id(self, id):
    #     self.id = ObjectId(id)
    #
    # def __repr__(self):
    #     return '<Thread %r>' % (self.title)
    #
    # def get_comments(self, order_by='timestamp'):
    #     """
    #     default order by timestamp
    #     return only top levels!
    #     """
    #     if order_by == 'timestamp':
    #         return self.comments.filter_by(depth=1).\
    #             order_by(db.desc(Comment.created_on)).all()[:THREAD.MAX_COMMENTS]
    #     else:
    #         return self.comments.filter_by(depth=1).\
    #             order_by(db.desc(Comment.created_on)).all()[:THREAD.MAX_COMMENTS]
    #
    # def get_status(self):
    #     """
    #     returns string form of status, 0 = 'dead', 1 = 'alive'
    #     """
    #     return THREAD.STATUS[self.status]
    #
    def get_age(self):
        """
        returns the raw age of this thread in seconds
        """
        return (self.date_created - datetime.datetime(1970, 1, 1)).total_seconds()

    def get_hotness(self):
        """
        returns the reddit hotness algorithm (votes/(age^1.5))
        """
        order = math.log(max(abs(self.num_votes), 1), 10) # Max/abs are not needed in our case
        seconds = self.get_age() - 1134028003
        return round(order + seconds / 45000, 6)

    def set_hotness(self):
        """
        returns the reddit hotness algorithm (votes/(age^1.5))
        """
        self.hotness = self.get_hotness()


    def pretty_date(self, typeof='created'):
        """
        returns a humanized version of the raw age of this thread,
        eg: 34 minutes ago versus 2040 seconds ago.
        """
        if typeof == 'created':
            return utils.pretty_date(self.date_created)
        elif typeof == 'updated':
            return utils.pretty_date(self.date_modified)

    def add_comment(self, comment_text, comment_parent_id, user_id):
        """
        add a comment to this particular thread
        """

        user = user_model.User.find_one({'id': ObjectId(user_id)})

        if comment_parent_id.strip().replace(" ",""):
            # parent_comment = Comment.query.get_or_404(comment_parent_id)
            # if parent_comment.depth + 1 > THREAD.MAX_COMMENT_DEPTH:
            #    flash('You have exceeded the maximum comment depth')
            app.logger.error("have parent?: {}".format(comment_parent_id))
            app.logger.debug(type(comment_parent_id))
            comment_parent_id = ObjectId(comment_parent_id)
            comment = Comment(thread_id=ObjectId(self.id),
                                user_id=user.id,
                                text=comment_text,
                                parent_id=comment_parent_id,
                                parent=Comment.find_one({"id":comment_parent_id}),
                                user=user,
                                thread=self,
                                date_created=datetime.datetime.now(),
                                date_modified=datetime.datetime.now())
        else:
            comment = Comment(thread_id=ObjectId(self.id),
                    user_id=ObjectId(user_id),
                    text=comment_text,
                    user=user,
                    thread=self,
                    date_created=datetime.datetime.now(),
                    date_modified=datetime.datetime.now())

        # db.session.add(comment)
        # db.session.commit()
        comment.commit()
        comment.set_depth()
        app.logger.debug("comment depth: {}".format(comment.depth))

        comment.commit()

        self.comments.append(comment)
        self.comment_ids.append(comment.id)
        return comment

    # def get_voter_ids(self):
    #     """
    #     return ids of users who voted this thread up
    #     """
    #     upvotes = ThreadUpvote.find({"thread_id":self.id})
    #     # rs = db.engine.execute(select)
    #     # ids = rs.fetchall() # list of tuples
    #     ids = [v.user_id for v in upvotes]
    #     return ids

    def has_voted(self, user_id):
        """
        did the user vote already
        """
        # select_votes = thread_upvotes.select(
        #         db.and_(
        #             thread_upvotes.c.user_id == user_id,
        #             thread_upvotes.c.thread_id == self.id
        #         )
        # )
        # rs = db.engine.execute(select_votes)

        select_votes = (ThreadUpvote
                        .find({"$and": [{"user_id": ObjectId(user_id)},
                          {"thread_id": self.id}]})).count()

        return False if select_votes == 0 else True

    def vote(self, user_id):
        """
        allow a user to vote on a thread. if we have voted already
        (and they are clicking again), this means that they are trying
        to unvote the thread, return status of the vote for that user
        """
        already_voted = self.has_voted(user_id)
        vote_status = None
        if not already_voted:
            # vote up the thread
            # db.engine.execute(
            #     thread_upvotes.insert(),
            #     user_id   = user_id,
            #     thread_id = self.id
            # )

            upvote_data = {
                    "user_id" : ObjectId(user_id),
                    "thread_id" : self.id
            }
            upvote = ThreadUpvote(**upvote_data)

            self.num_votes = self.num_votes + 1
            vote_status = True
        else:
            # unvote the thread
            # db.engine.execute(
            #     thread_upvotes.delete(
            #         db.and_(
            #             thread_upvotes.c.user_id == user_id,
            #             thread_upvotes.c.thread_id == self.id
            #         )
            #     )
            # )

            query = {"$and":[{"userid":ObjectId(user_id)},
                            {"thread_id":self.id}]}
            upvote = ThreadUpvote.remove(query)

            self.num_votes = self.num_votes - 1
            vote_status = False

        app.logger.debug("vote_status: {}".format(vote_status))
        upvote.commit()

        self.commit()
        # db.session.commit() # for the vote count
        return vote_status

    def extract_thumbnail(self):
        """
        ideally this type of heavy content fetching should be put on a
        celery background task manager or at least a crontab.. instead of
        setting it to run literally as someone posts a thread. but once again,
        this repo is just a simple example of a reddit-like crud application!
        """
        DEFAULT_THUMBNAIL = 'https://reddit.codelucas.com/static/imgs/reddit-camera.png'
        if self.link:
            thumbnail = media.get_top_img(self.link)
        if not thumbnail:
            thumbnail = DEFAULT_THUMBNAIL
        self.thumbnail = thumbnail
        self.commit()

    def get_comments(self):
        app.logger.debug(list(Comment.find({"thread_id":self.id})))
        return list(Comment.find({"thread_id":self.id}))

    def get_comment_count(self):
        return Comment.find({"thread_id":self.id}).count()


@instance.register
class Comment(Document):
    """
    This class is here because comments can only be made on threads,
    so it is contained completly in the threads module.

    Note the parent_id and children values. A comment can be commented
    on, so a comment has a one to many relationship with itself.

    Backrefs:
        A comment can refer to its parent thread with 'thread'
        A comment can refer to its parent comment (if exists) with 'parent'
    """
    # __tablename__ = 'threads_comment'

    text = fields.StringField(default=None,
                               validate=validate.Length(max=THREAD.MAX_BODY))

    user_id = fields.ObjectIdField() # Integer?
    thread_id = fields.ObjectIdField() # Integer?

    user = fields.ReferenceField("User") # Integer?
    thread = fields.ReferenceField("Thread") # Integer?

    parent_id = fields.ObjectIdField(missing=None)
    # children = fields.ReferenceField('Comment')
    parent = fields.ReferenceField('Comment', missing=None)

    depth = fields.IntField( default=1, missing=1) # start at depth 1

    date_created = fields.DateTimeField(default=datetime.datetime.now(),
                                        missing=datetime.datetime.now())
    date_modified = fields.DateTimeField(
        default=datetime.datetime.now(),
        missing=datetime.datetime.now())

    num_votes = fields.IntegerField(default=0, missing=0)


    class Meta:
        collection_name = 'comments'

    def update(self):
        if not self.date_created:
            self.date_created = datetime.datetime.now()
        self.date_modified = datetime.datetime.now()
        # self.thread = self.get_thread()
        return self


    def __repr__(self):
        return '<Comment %r>' % (self.text[:25])

    # def __init__(self, thread_id, user_id, text, parent_id=None):
    #     self.thread_id = thread_id
    #     self.user_id = user_id
    #     self.text = text
    #     self.parent_id = parent_id
    #
    # def get_comment(self):
    #     comment = {"thread_id": self.thread_id,
    #               "user_id" : self.user_id,
    #               "text": self.text,
    #               "parent_id": self.parent_id,
    #               }
    #     return comment

    # def get_all_children(self):
    #     def get_children(parent_id, children=[]):
    #         children += Comment.find({"parent_id":parent_id})
    #         return children
    #
    #     def recursive_children(parent_id, children=[]):
    #         if children:
    #             for c in children:
    #                 return recursive_children(c.id)
    #
    #     for c in get_children():
    #         recursive_children(parent_id, children)
    #
    #     for c in Comment.find({"parent_id":parent_id}):
    #         children += get_children(c.id, children=children)
    #
    #     parent_id = copy.copy(self.id)
    #     Comment.find({"parent_id": self.id})
    #
    #     children = Comment.find({"parent_id":parent_id})
    #
    #     grandchildren = copy.copy(children)
    #     for child in copy.copy(children):
    #         grandchildren += get_recursive_children(child,

    def get_children(self):
        return Comment.find({"parent_id": self.id})

    def get_children_count(self):
        return self.get_children().count()

    def set_depth(self):
        """
        call after initializing
        """
        app.logger.debug("comments: {}".format([x for x in Comment.find()]))
        app.logger.debug("comments: {}".format(list(Comment.find())))
        for c in Comment.find():
            app.logger.debug("comment: {}".format(c))
            app.logger.debug("self.id, parent.id: {}".format((self.id, self.parent_id)))


        num_children = self.get_children_count()
        app.logger.debug("num_children: {}".format(num_children))
        app.logger.debug("children: \n{}".format([x for x in self.get_children()]))
        # if num_children > 0:
        if self.parent is not None:
            self.depth = self.parent.fetch().depth + 1
            self.commit()

    def get_comments(self, order_by='timestamp'):
        """
        default order by timestamp

        Note:
            Only getting depth = 1 comments for simplicity
        """
        app.logger.debug("in comments model.get_comments")
        if order_by == 'timestamp':
            # return self.children.order_by(db.desc(Comment.created_on)).\
            #     all()[:THREAD.MAX_COMMENTS]
            comments = (Comment.find({"parent_id":self.id})
                .sort([("date_created", pymongo.ASCENDING)])
                [:THREAD.MAX_COMMENTS])
            app.logger.debug(comments)
            return comments
        else:
            # return self.comments.order_by(db.desc(Comment.created_on)).\
            #     all()[:THREAD.MAX_COMMENTS]
            comments =  (Comment.find({"parent_id":self.id}).sort(
                [("date_created", pymongo.DESCENDING)])
                [:THREAD.MAX_COMMENTS])
            app.logger.debug(comments)
            return comments

    def get_margin_left(self):
        """
        nested comments are pushed right on a page
        -15px is our default margin for top level comments
        """
        margin_left = 15 + ((self.depth-1) * 32)
        margin_left = min(margin_left, 680)
        return str(margin_left) + "px"

    def get_age(self):
        """
        returns the raw age of this thread in seconds
        """
        return (self.date_created - datetime.datetime(1970,1,1)).total_seconds()

    def pretty_date(self, typeof='created'):
        """
        returns a humanized version of the raw age of this thread,
        eg: 34 minutes ago versus 2040 seconds ago.
        """
        if typeof == 'created':
            return utils.pretty_date(self.date_created)
        elif typeof == 'updated':
            return utils.pretty_date(self.date_modified)

    def vote(self, direction):
        """
        """
        pass

    def comment_on(self):
        """
        when someone comments on this particular comment
        """
        pass

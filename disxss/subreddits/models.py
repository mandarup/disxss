# -*- coding: utf-8 -*-
"""
All database abstractions for subreddits go in this file.

"""
import datetime


from bson.objectid import ObjectId

from umongo import Instance, Document, fields, ValidationError, set_gettext
from umongo import validate
from umongo.marshmallow_bonus import SchemaFromUmongo

from disxss import db
from disxss.threads import constants as THREAD
from disxss import utils
from disxss import media
from disxss import instance
from disxss.subreddits import constants as SUBREDDIT
from disxss.threads import models as threads_model


@instance.register
class Subreddit(Document):
    """
    """
    # __tablename__ = 'subreddits_subreddit'
    # id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String(SUBREDDIT.MAX_NAME), unique=True)
    name = fields.StrField(validate=validate.Length(max=SUBREDDIT.MAX_NAME),
                            unique=True)

    # desc = db.Column(db.String(SUBREDDIT.MAX_DESCRIPTION))
    desc = fields.StrField(validate=validate.Length(max=SUBREDDIT.MAX_DESCRIPTION))

    # admin_id = db.Column(db.Integer, db.ForeignKey('users_user.id'))
    admin_id  = fields.ReferenceField("User")

    # created_on = db.Column(db.DateTime, default=db.func.now())
    # updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    date_created = fields.DateTimeField(default=datetime.datetime.now())
    date_updated = fields.DateTimeField(default=datetime.datetime.now())

    # threads = db.relationship('Thread', backref='subreddit', lazy='dynamic')
    # threads = fields.ReferenceField("Thread") # Integer?

    # status = db.Column(db.SmallInteger, default=SUBREDDIT.ALIVE)
    status = fields.IntegerField(default=SUBREDDIT.ALIVE)

    class Meta:
        collection_name = 'subreddits'
        # collection = db.subreddits

    def __repr__(self):
        return '<Subreddit %r>' % (self.name)


    def get_threads(self, order_by='timestamp'):
        """
        default order by timestamp
        """
        # if order_by == 'timestamp':
        #     return self.threads.order_by(db.desc(Thread.created_on)).\
        #         all()[:SUBREDDIT.MAX_THREADS]
        # else:
        #     return self.threads.order_by(db.desc(Thread.created_on)).\
        #         all()[:SUBREDDIT.MAX_THREADS]

        threads = threads_model.Thread.find({'subreddit_id':self.id})#[:SUBREDDIT.MAX_THREADS]
        return threads

    # def get_status(self):
    #     """
    #     returns string form of status, 0 = 'dead', 1 = 'alive'
    #     """
    #     return SUBREDDIT.STATUS[self.status]
    #
    # def get_age(self):
    #     """
    #     returns the raw age of this subreddit in seconds
    #     """
    #     return (self.created_on - datetime.datetime(1970, 1, 1)).total_seconds()
    #
    # def pretty_date(self, typeof='created'):
    #     """
    #     returns a humanized version of the raw age of this subreddit,
    #     eg: 34 minutes ago versus 2040 seconds ago.
    #     """
    #     if typeof == 'created':
    #         return utils.pretty_date(self.created_on)
    #     elif typeof == 'updated':
    #         return utils.pretty_date(self.updated_on)
    # """
    # def add_thread(self, comment_text, comment_parent_id, user_id):
    #     if len(comment_parent_id) > 0:
    #         comment_parent_id = int(comment_parent_id)
    #         comment = Comment(thread_id=self.id, user_id=user_id,
    #                 text=comment_text, parent_id=comment_parent_id)
    #     else:
    #         comment = Comment(thread_id=self.id, user_id=user_id,
    #                 text=comment_text)
    #
    #     db.session.add(comment)
    #     db.session.commit()
    #     comment.set_depth()
    #     return comment
    # """

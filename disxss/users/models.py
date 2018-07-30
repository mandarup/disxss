"""User Model.
"""

import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from disxss.users import constants as USER

# TODO: threads import
# from disxss.threads.models import thread_upvotes, comment_upvotes


from pymodm import MongoModel, EmbeddedMongoModel, fields, connect
from pymodm.queryset import QuerySet
from pymodm.manager import Manager

class UserQuerySet(QuerySet):
    pass

#     # def __init__(self, *args, **kwargs):
#     #     super().__init__(*args, **kwargs)
#
#     def active(self):
#         '''Return only active users.'''
#         return self.raw({"status": 1})

    # def get_status(self):
    #     """
    #     returns string form of status, 0 = 'dead', 1 = 'alive'
    #     """
    #     return USER.STATUS[self.status]
    #
    # def get_role(self):
    #     """
    #     analogous to above but for roles
    #     """
    #     return USER.ROLE[self.role]
    #
    def get_thread_karma(self):
        """
        fetch the number of votes this user has had on his/her threads

        1.) Get id's of all threads by this user

        2.) See how many of those threads also were upvoted but not by
        the person him/her self.
        """
        # thread_ids = [t.id for t in self.threads]
        # select = thread_upvotes.select(db.and_(
        #         thread_upvotes.c.thread_id.in_(thread_ids),
        #         thread_upvotes.c.user_id != self.id
        #     )
        # )
        # rs = db.engine.execute(select)
        # return rs.rowcount
        # TODO

        return 0

    def get_comment_karma(self):
        """
        fetch the number of votes this user has had on his/her comments

        """
        # TODO

        return 0





class User(MongoModel):
    # Make all these fields required, so that if we try to save a User instance
    # that lacks one of these fields, we'll get a ValidationError, which we can
    # catch and render as an error on a form.
    #
    # Use the email as the "primary key" (will be stored as `_id` in MongoDB).
    email = fields.EmailField(primary_key=True, required=True)
    # email = fields.EmailField(primary_key=False, required=True)
    username = fields.CharField(required=True)
    # `password` here will be stored in plain text! We do this for simplicity of
    # the example, but this is not a good idea in general. A real authentication
    # system should only store hashed passwords, and queries for a matching
    # user/password will need to hash the password portion before of the query.
    password = fields.CharField(required=True)

    created_at = fields.DateTimeField(default=datetime.datetime.now())
    modified_at = fields.DateTimeField(default=datetime.datetime.now())
    status = fields.IntegerField(default=USER.ALIVE)
    role = fields.IntegerField(default=USER.USER)

    objects = Manager.from_queryset( UserQuerySet)()

    # def __init__(self,
    #             # *args,
    #             email=None, password=None,
    #             username=None, created_at=None,
    #             modified_at=None,
    #             status=None,
    #             role=None
    #             ):
    #     pass

        # self.set_password(password)

        # users = Manager.from_queryset( UserQuerySet)

    # TODO:
    # define getters for comments, threads, subreddits

    # def set_password(self, password):
    #     self.password = generate_password_hash(password)
    #
    # def check_password(self, password):
    #     return check_password_hash(self.password, password)

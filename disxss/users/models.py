"""User Model.
"""

import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from umongo import Instance, Document, fields, ValidationError, set_gettext
from umongo import validate
from umongo.marshmallow_bonus import SchemaFromUmongo



from disxss.users import constants as USER

# TODO: threads import
# from disxss.threads.models import thread_upvotes, comment_upvotes
from disxss import db
from disxss import app
from disxss import instance


# users = db.users


# class UserQuerySet(QuerySet):
#     pass
#
# #     # def __init__(self, *args, **kwargs):
# #     #     super().__init__(*args, **kwargs)
# #
#     def active(self):
#         '''Return only active users.'''
#         return self.raw({"status": 1})
#
#     def get_status(self):
#         """
#         returns string form of status, 0 = 'dead', 1 = 'alive'
#         """
#         return USER.STATUS[self.status]
#
#     def get_role(self):
#         """
#         analogous to above but for roles
#         """
#         return USER.ROLE[self.role]
#     #
#     def get_thread_karma(self):
#         """
#         fetch the number of votes this user has had on his/her threads
#
#         1.) Get id's of all threads by this user
#
#         2.) See how many of those threads also were upvoted but not by
#         the person him/her self.
#         """
#         # thread_ids = [t.id for t in self.threads]
#         # select = thread_upvotes.select(db.and_(
#         #         thread_upvotes.c.thread_id.in_(thread_ids),
#         #         thread_upvotes.c.user_id != self.id
#         #     )
#         # )
#         # rs = db.engine.execute(select)
#         # return rs.rowcount
#         # TODO
#
#         return 0
#
#     def get_comment_karma(self):
#         """
#         fetch the number of votes this user has had on his/her comments
#
#         """
#         # TODO
#
#         return 0





# class User(MongoModel):
#     # Make all these fields required, so that if we try to save a User instance
#     # that lacks one of these fields, we'll get a ValidationError, which we can
#     # catch and render as an error on a form.
#     #
#     # Use the email as the "primary key" (will be stored as `_id` in MongoDB).
#     email = fields.EmailField(primary_key=True, required=True)
#     # email = fields.EmailField(primary_key=False, required=True)
#     username = fields.CharField(required=True)
#     # `password` here will be stored in plain text! We do this for simplicity of
#     # the example, but this is not a good idea in general. A real authentication
#     # system should only store hashed passwords, and queries for a matching
#     # user/password will need to hash the password portion before of the query.
#     password = fields.CharField(required=True)
#
#     created_at = fields.DateTimeField(default=datetime.datetime.datetime.now())
#     modified_at = fields.DateTimeField(default=datetime.datetime.datetime.now())
#     status = fields.IntegerField(default=USER.ALIVE)
#     role = fields.IntegerField(default=USER.USER)
#
#     objects = Manager.from_queryset( UserQuerySet)()
#
#     class Meta:
#         write_concern = WriteConcern(j=True)
#         connection_alias = 'disxss'
#
#     # def __init__(self,
#     #             # *args,
#     #             email=None, password=None,
#     #             username=None, created_at=None,
#     #             modified_at=None,
#     #             status=None,
#     #             role=None
#     #             ):
#     #     pass
#
#         # self.set_password(password)
#
#         # users = Manager.from_queryset( UserQuerySet)
#
#     # TODO:
#     # define getters for comments, threads, subreddits
#
#     # def set_password(self, password):
#     #     self.password = generate_password_hash(password)
#     #
#     # def check_password(self, password):
#     #     return check_password_hash(self.password, password)




# class User(object):
#     # email = fields.EmailField(primary_key=True, required=True)
#     # # email = fields.EmailField(primary_key=False, required=True)
#     # username = fields.CharField(required=True)
#     # # `password` here will be stored in plain text! We do this for simplicity of
#     # # the example, but this is not a good idea in general. A real authentication
#     # # system should only store hashed passwords, and queries for a matching
#     # # user/password will need to hash the password portion before of the query.
#     # password = fields.CharField(required=True)
#     #
#     # created_at = fields.DateTimeField(default=datetime.datetime.datetime.now())
#     # modified_at = fields.DateTimeField(default=datetime.datetime.datetime.now())
#     # status = fields.IntegerField(default=USER.ALIVE)
#     # role = fields.IntegerField(default=USER.USER)
#
#     __private = ['password']
#
#     def __init__(self,
#             email=None,
#             username=None,
#             created_at=datetime.datetime.datetime.now(),
#             modified_at=datetime.datetime.datetime.now(),
#             password = None,
#             document=None
#             ):
#
#         if document is not None:
#             self._set(document)
#         else:
#             self.email = email
#             self.username = username
#             self.created_at = created_at
#             self.modified_at = modified_at
#             self.password = password
#             self.set_status_active()
#             self._set()
#
#
#
#     def _set(self, document=None):
#         if document is not None:
#             # for k,v in document.items():
#             #     setattr(self, k, v)
#             app.logger.debug(document)
#             self._document = document
#             self.__set()
#         else:
#             self._document = {"email" : self.email,
#                     "username" : self.username,
#                     "created_at" : self.created_at,
#                     "modified_at" : self.modified_at,
#                     "status": self.status,
#                     "password": self.password}
#         return self
#
#     def __set(self):
#         for k,v in self._document.items():
#             # if k not in self.__private:
#             if k == '_id':
#                 setattr(self, k, str(v))
#                 continue
#             setattr(self, k, v)
#
#     def get(self):
#         return self._document
#
#     def set_status_active(self):
#         self.status = 1
#
#     def save(self):
#         self._id = users.insert_one(self.get()).inserted_id
#         return self
#
#
#
#     def get_status(self):
#         """
#         returns string form of status, 0 = 'dead', 1 = 'alive'
#         """
#         return USER.STATUS[users.find({'username':self.user['username']})['status']]
#
#
#     def get_role(self):
#         """
#         analogous to above but for roles
#         """
#         return USER.ROLE[users.find({'role':self.user['role']})]
#
#
#     @staticmethod
#     def active_users():
#         '''Return only active users.'''
#         return users.find({"status": 1})
#
#
#     def get_thread_karma(self):
#         """
#         fetch the number of votes this user has had on his/her threads
#
#         1.) Get id's of all threads by this user
#
#         2.) See how many of those threads also were upvoted but not by
#         the person him/her self.
#         """
#         # thread_ids = [t.id for t in self.threads]
#         # select = thread_upvotes.select(db.and_(
#         #         thread_upvotes.c.thread_id.in_(thread_ids),
#         #         thread_upvotes.c.user_id != self.id
#         #     )
#         # )
#         # rs = db.engine.execute(select)
#         # return rs.rowcount
#         # TODO
#
#         return 0
#
#     def get_comment_karma(self):
#         """
#         fetch the number of votes this user has had on his/her comments
#
#         """
#         # TODO
#
#         return 0
#
#     # def threads(self):
#     #     user.find("threads")



@instance.register
class User(Document):
    username = fields.StrField(required=True, unique=True)
    email = fields.EmailField(required=True, unique=True)
    firstname = fields.StrField()
    lastname = fields.StrField()
    # birthday = fields.DateTimeField()
    birthday = fields.DateTimeField(validate=validate.Range(min=datetime.datetime(1900, 1, 1)))
    password = fields.StrField(required=True)  # Don't store it in clear in real life !
    date_created = fields.DateTimeField(default=datetime.datetime.now())
    date_modified = fields.DateTimeField(default=datetime.datetime.now())
    # authored_docs = fields.ListField(fields.ReferenceField("Paper"))

    def update(self, *args, **kwargs):
        if not self.date_created:
            self.date_created = datetime.datetime.now()
        self.date_modified = datetime.datetime.now()
        return super(User, self).update(*args, **kwargs)

    class Meta:
        collection = db.user

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

    # def threads(self):
    #     user.find("threads")


# Create a custom marshmallow schema from User document in order to avoid some fields
class UserNoPassSchema(User.schema.as_marshmallow_schema()):
    class Meta:
        read_only = ('password',)
        load_only = ('password',)

no_pass_schema = UserNoPassSchema()

def dump_user_no_pass(u):
    return no_pass_schema.dump(u).data



def populate_db():
    print('populating db')
    User.collection.drop()
    User.ensure_indexes()
    for data in [
        {
            'username': 'mze',
            'email':'a@b.com',
            'lastname': 'Mao',
            'firstname': 'Zedong',
            'birthday': datetime.datetime(1893, 12, 26),
            'password': 'Serve the people'
        },

        {
            'nick': 'xiji',
            'email':'c@d.com',
            'lastname': 'Xi',
             'firstname': 'Jinping',
            'birthday': datetime.datetime(1953, 6, 15),
             'password': 'Achieve the 4 modernisations',
            'date_created' : datetime.datetime.utcnow()
        }
    ]:
        User(**data).commit()


from disxss import  db

# users = db.user


def get_status(user):
    """
    returns string form of status, 0 = 'dead', 1 = 'alive'
    """
    return USER.STATUS[users.find({'username':user['username']})['status']]

def get_role(user):
    """
    analogous to above but for roles
    """
    return USER.ROLE[users.find({'role':user['role']})]


def active_users(self):
    '''Return only active users.'''
    return users.find({"status": 1})


def get_thread_karma(user):
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

def get_comment_karma(user):
    """
    fetch the number of votes this user has had on his/her comments

    """
    # TODO

    return 0

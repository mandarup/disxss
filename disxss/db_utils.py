
import datetime

from disxss.users.models import User
from disxss.threads.models import Thread
from disxss.threads.models import Comment
from disxss.threads.models import CommentUpvote
from disxss.threads.models import ThreadUpvote
from disxss.subreddits.models import Subreddit


def init_db():

    try:
        User.collection.drop()
    except Exception as e:
        print(str(e))
    User.ensure_indexes()


    try:
        Thread.collection.drop()
    except Exception as e:
        print(str(e))
    Thread.ensure_indexes()

    try:
        Comment.collection.drop()
    except Exception as e:
        print(str(e))
    Comment.ensure_indexes()

    try:
        CommentUpvote.collection.drop()
    except Exception as e:
        print(str(e))

    CommentUpvote.ensure_indexes()


    try:
        ThreadUpvote.collection.drop()
    except Exception as e:
        print(str(e))


    ThreadUpvote.ensure_indexes()

    try:
        Subreddit.collection.drop()
    except Exception as e:
        print(str(e))
    Subreddit.ensure_indexes()


def populate_db():
    User.collection.drop()
    User.ensure_indexes()


    for data in [
        {
            'username': 'a',
            'email':'a@b.io',
            'lastname': 'Mao',
            'firstname': 'Zedong',
            'birthday': datetime.datetime(1993, 12, 26),
            'password': '1'
        },

        {
            'username': 'xiji',
            'email':'c@d.com',
            'lastname': 'Xi',
             'firstname': 'Jinping',
            'birthday': datetime.datetime(1953, 6, 15),
             'password': 'Achieve the 4 modernisations',
            'date_created' : datetime.datetime.utcnow()
        }
    ]:
        User(**data).commit()



def paginate(collection, page_size=10, page_num=1):
    """returns a set of documents belonging to page number `page_num`
    where size of each page is `page_size`.
    """
    # Calculate number of documents to skip
    skips = page_size * (page_num - 1)

    # Skip and limit
    cursor = collection.skip(skips).limit(page_size)

    # Return documents
    return [x for x in cursor]


import datetime
from werkzeug import check_password_hash, generate_password_hash

from disxss.users.models import User
from disxss.threads.models import Thread
from disxss.threads.models import Comment
from disxss.threads.models import CommentUpvote
from disxss.threads.models import ThreadUpvote
from disxss.categories.models import Category


def init_db():

    try:
        User.collection.drop()
    except Exception as e:
        print(str(e))
    User.ensure_indexes()

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
        Category.collection.drop()
    except Exception as e:
        print(str(e))
    Category.ensure_indexes()


def populate_db():
    # User.collection.drop()
    # User.ensure_indexes()


    for data in [
        {
            'username': 'a',
            'email':'a@disxss.io',
            'lastname': 'Mao',
            'firstname': 'Zedong',
            'birthday': datetime.datetime(1993, 12, 26),
            'password': generate_password_hash('1')
        },

        {
            'username': 'b',
            'email':'b@disxss.io',
            'lastname': 'Xi',
             'firstname': 'Jinping',
            'birthday': datetime.datetime(1953, 6, 15),
             'password': generate_password_hash('1'),
            'date_created' : datetime.datetime.utcnow()
        }
    ]:
        User(**data).commit()

    a_user = User.find_one()
    _new_category = {"name":"test_category",
                        "desc":"test desc",
                        "admin_id":a_user.id,
                        "admin": a_user}
    new_category = Category(**_new_category)
    new_category.commit()


    thread_data = {"title":"test thread", "link":"disxss.com",
            "text":"not alive",
            "user_id":a_user.id,
            "category_id":Category.find_one().id,
            "user": a_user,
            "category": Category.find_one()}
    thread = Thread(**thread_data)
    thread.update()
    thread.commit()

    # login user
    


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

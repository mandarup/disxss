# -*- coding: utf-8 -*-
"""
Simple module for searching the sql-alchemy database based
on user queries.
"""
from disxss.threads.models import Thread, Comment
from disxss import app
# from flask_reddit import db


def search(query, orderby='date_created', filter_user=None, search_title=True,
            search_text=True, category=None, limit=100):
    """
    search for threads (and maybe comments in the future)
    """
    if not query:
        return []
    query = query.strip()
    base_query = '%' + query + '%'

    app.logger.debug("query: {}".format(query))
    # base_qs = Thread

    # title_clause = Thread.title.like(base_query) if search_title else False
    # text_clause = Thread.text.like(base_query) if search_text else False

    # Thread.create_index([('title', 'title')])
    # Thread.create_indexes([('title', 'text'), ('text', 'text')])

    # title_clause = Thread.find({"$text": {"$search": base_query}})

    # Thread.create_index([('textfield', 'text')])
    # text_clause = Thread.find({"text": {"$search": base_query}})


    query_res = Thread.find({"$text": {"$search": base_query}})


    # TODO: Searching by category requires joining, leave out for now.
    # category_clause = Thread.category.name.like(category.name) if category else False

    # or_clause = db.or_(title_clause, text_clause)

    # base_qs = base_qs.filter(or_clause)

    # if orderby == 'creation':
    #     base_qs = base_qs.order_by(db.desc(Thread.created_on))
    # elif orderby == 'title':
    #     base_qs = base_qs.order_by(Thread.title)
    # elif orderby == 'numb_comments':
    #     pass

    # base_qs = base_qs.limit(limit)

    base_qs = query_res.limit(limit)
    return base_qs

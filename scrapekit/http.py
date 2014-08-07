
from requests import Session as RequestsSession


def Session():
    # TODO, consider using CacheControl, or write a new
    # cache tool.
    # TODO, restore method signatures somehow?
    return RequestsSession()


def get(*a, **kw):
    # TODO, restore method signatures somehow?
    session = Session()
    return session.get(*a, **kw)


def post(*a, **kw):
    session = Session()
    return session.get(*a, **kw)


def put(*a, **kw):
    session = Session()
    return session.get(*a, **kw)


def head(*a, **kw):
    session = Session()
    return session.get(*a, **kw)

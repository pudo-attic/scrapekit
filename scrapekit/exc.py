

class ScraperException(Exception):
    """ Generic scraper exception, the base for all other exceptions.
    """


class WrappedMixIn():
    """ Mix-in for wrapped exceptions. """

    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.message = wrapped.message

    def __repr__(self):
        name = self.__class__.__name__
        return '<%s(%s)>' % (name, self.wrapped)


class DependencyException(ScraperException, WrappedMixIn):
    """ Triggered when an operation would require the installation
    of further dependencies. """


class ParseException(ScraperException, WrappedMixIn):
    """ Triggered when parsing an HTTP response into the desired
    format (e.g. an HTML DOM, or JSON) is not possible. """

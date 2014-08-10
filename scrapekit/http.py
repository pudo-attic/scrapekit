import os

import requests
from cachecontrol import CacheControl
from cachecontrol.caches import FileCache

from scrapekit.exc import DependencyException, ParseException


class ScraperResponse(requests.Response):
    """ A modified scraper response that can parse the content into
    HTML, XML, JSON or a BeautifulSoup instance. """

    def html(self):
        """ Create an ``lxml``-based HTML DOM from the response. The tree
        will not have a root, so all queries need to be relative
        (i.e. start with a dot).
        """
        try:
            from lxml import html
            return html.fromstring(self.content)
        except ImportError, ie:
            raise DependencyException(ie)

    def xml(self):
        """ Create an ``lxml``-based XML DOM from the response. The tree
        will not have a root, so all queries need to be relative
        (i.e. start with a dot).
        """
        try:
            from lxml import etree
            return etree.fromstring(self.content)
        except ImportError, ie:
            raise DependencyException(ie)

    def json(self, **kwargs):
        """ Create JSON object out of the response. """
        try:
            return super(ScraperResponse, self).json(**kwargs)
        except ValueError, ve:
            raise ParseException(ve)


class ScraperSession(requests.Session):
    """ Sub-class requests session to be able to introduce additional
    state to sessions and responses. """

    def request(self, method, url, **kwargs):
        orig = super(ScraperSession, self).request(method, url, **kwargs)
        self.scraper.log.debug("%s %s", method, url, extra={
            'reqMethod': method,
            'reqUrl': url,
            'reqArgs': kwargs
            })
        response = ScraperResponse()
        response.__setstate__(orig.__getstate__())
        return response


def make_session(scraper):
    """ Instantiate a session with the desired configuration parameters,
    including the cache policy. """
    cache_path = os.path.join(scraper.config.data_path, 'cache')
    cache_policy = scraper.config.cache_policy
    cache_policy = cache_policy.lower().strip()
    session = ScraperSession()
    session.scraper = scraper
    if cache_policy == 'http':
        session = CacheControl(session,
                               cache=FileCache(cache_path))
    return session

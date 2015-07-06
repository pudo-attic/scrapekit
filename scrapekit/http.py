import os

import requests
from cachecontrol.adapter import CacheControlAdapter
from cachecontrol.caches import FileCache
from cachecontrol.controller import CacheController

from scrapekit.exc import DependencyException, ParseException


CARRIER_HEADER = 'X-Scrapekit-Cache-Policy'


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
        except ImportError as ie:
            raise DependencyException(ie)

    def xml(self):
        """ Create an ``lxml``-based XML DOM from the response. The tree
        will not have a root, so all queries need to be relative
        (i.e. start with a dot).
        """
        try:
            from lxml import etree
            return etree.fromstring(self.content)
        except ImportError as ie:
            raise DependencyException(ie)

    def json(self, **kwargs):
        """ Create JSON object out of the response. """
        try:
            return super(ScraperResponse, self).json(**kwargs)
        except ValueError as ve:
            raise ParseException(ve)


class ScraperSession(requests.Session):
    """ Sub-class requests session to be able to introduce additional
    state to sessions and responses. """

    def request(self, method, url, cache=None, **kwargs):
        # decide the cache policy and place it in a fake HTTP header
        cache_policy = cache or self.cache_policy
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers'][CARRIER_HEADER] = cache_policy

        # TODO: put UA fakery here.

        orig = super(ScraperSession, self).request(method, url, **kwargs)

        # log request details to the JSON log
        self.scraper.log.debug("%s %s", method, url, extra={
            'reqMethod': method,
            'reqUrl': url,
            'reqArgs': kwargs
            })

        # Cast the response into our own subclass which has HTML/XML
        # parsing support.
        response = ScraperResponse()
        response.__setstate__(orig.__getstate__())
        return response


class PolicyCacheController(CacheController):
    """ Switch the caching mode based on the caching policy provided by
    request, which in turn can be given at request time or through the
    scraper configuration. """

    def cached_request(self, request):
        cache_policy = request.headers.pop(CARRIER_HEADER, 'none')
        if cache_policy == 'force' or cache_policy is True:
            # Force using the cache, even if HTTP semantics forbid it.
            cache_url = self.cache_url(request.url)
            resp = self.serializer.loads(request, self.cache.get(cache_url))
            return resp or False
        elif cache_policy == 'http':
            return super(PolicyCacheController, self).cached_request(request)
        else:
            return False


def make_session(scraper):
    """ Instantiate a session with the desired configuration parameters,
    including the cache policy. """
    cache_path = os.path.join(scraper.config.data_path, 'cache')
    cache_policy = scraper.config.cache_policy
    cache_policy = cache_policy.lower().strip()
    session = ScraperSession()
    session.scraper = scraper
    session.cache_policy = cache_policy

    adapter = CacheControlAdapter(
        FileCache(cache_path),
        cache_etags=True,
        controller_class=PolicyCacheController
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

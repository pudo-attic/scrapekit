import os

import requests
from cachecontrol import CacheControl
from cachecontrol.caches import FileCache


class ScraperResponse(requests.Response):
    pass


class ScraperSession(requests.Session):
    """ Sub-class requests session to be able to introduce additional
    state to sessions and responses. """

    def request(self, method, url, **kwargs):
        orig = super(ScraperSession, self).request(method, url, **kwargs)
        response = ScraperResponse()
        response.__setstate__(orig.__getstate__())
        return response


def make_session(scraper):
    """ Instantiate a session with the desired configuration parameters,
    including the cache policy. """
    cache_path = os.path.join(scraper.config.data_path, 'cache')
    session = ScraperSession()
    session = CacheControl(session,
                           cache=FileCache(cache_path))
    return session

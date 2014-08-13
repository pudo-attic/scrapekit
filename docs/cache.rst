Caching
=======

Caching of response data is implemented via `CacheControl
<https://github.com/ionrock/cachecontrol>`_, a library that extends
`requests <http://python-requests.org>`_. To enable a flexible usage of
the caching mechanism, the use of cached data is steered through a cache
policy, which can be specified either for the whole scraper or for a
specific request.

The following policies are supported:

* ``http`` will perform response caching and validation according to HTTP
  semantic, i.e. in the way that a browser would do it. This requires the
  server to set accurate cache control headers - which many applications
  are too stupid to do.
* ``none`` will disable caching entirely and always revert to the server for
  up-to-date information.
* ``force`` will always use the cached data and not check with the server
  for updated pages. This is useful in debug mode, but dangerous when used
  in production.

Per-request cache settings
--------------------------

While caching will usually be configured on a scraper-wide basis, it can
also be set for individual (``GET``) requests by passing a ``cache``
argument set to one of the policy names:

.. code-block:: python

  import scrapekit
  scraper = scrapekit.Scraper('example')

  # No caching:
  scraper.get('http://google.com', cache='none')

  # Cache according to HTTP semantics:
  scraper.get('http://google.com', cache='http')

  # Force re-use of data, even if it is stale:
  scraper.get('http://google.com', cache='force')

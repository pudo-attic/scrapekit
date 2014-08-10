Configuration
=============

Scrapekit supports a broad range of configuration options, which can be
set either via a configuration file, environment variables or
programmatically at run-time.


Configuration methods
---------------------

As a first source of settings, scrapekit will attempt to read a per-user
configuration file, ``~/.scrapekit.ini``. Inside the ini file, two
sections will be read: ``[scrapekit]`` is expected to hold general
settings, while a section, named after the current scraper, can be used to
adapt these settings: 

.. code-block:: ini

  [scrapekit]
  reports_path = /var/www/scrapers/reports

  [craigslist-sf-boats]
  threads = 5

After evaluating these settings, environment variables will be read (see
below for their names). Finally, all of these settings will be overridden
by any configuration provided to the constructor of
:py:class:`Scraper <scrapekit.core.Scraper>`.


Available settings
------------------

============ ====================== ====================================
Name         Environment variable   Description
============ ====================== ====================================
threads      SCRAPEKIT_THREADS      Number of threads to be started.
cache_policy SCRAPEKIT_CACHE_POLICY Policy for caching requests. Valid 
                                    values are ``disable`` (no caching),
                                    ``http`` (cache according to HTTP
                                    header semantics) and ``force``, to
                                    force local storage and re-use of
                                    any requests.
data_path    SCRAPEKIT_DATA_PATH    A storage directory for cached data 
                                    from HTTP requests. This is set to 
                                    be a temporary directory by default,
                                    which means caching will not work.
reports_path SCRAPEKIT_REPORTS_PATH A directory to hold log files and -
                                    if generated - the reports for this
                                    scraper.
============ ====================== ====================================


Custom settings
---------------

The scraper configuration is not limited to loading the settings
indicated above. Hence, custom configuration settings (e.g. for site
credentials) can be added to the ini file and then retrieved from the
``config`` attribute of a :py:class:`Scraper <scrapekit.core.Scraper>`
instance.

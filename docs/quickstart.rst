Quickstart
==========

Welcome to the scrapekit quickstart tutorial. In the following section, 
I'll show you how to write a simple scraper using the functions in
scrapekit.

Like many people, I've had a life-long, hidden desire to become a sail 
boat captain. To help me live the dream, we'll start by scraping
`Craigslist boat sales in San Francisco <https://sfbay.craigslist.org/boo/>`_.


Getting started
---------------

First, let's make a simple Python module, e.g. in a file called
``scrape_boats.py``.

.. code-block:: python

  import scrapekit

  scraper = scrapekit.Scraper('craigslist-sf-boats')

The first thing we've done is to instantiate a scraper and to give it
a name. The name will later be used to configure the scraper and to
read it's log ouput. Next, let's scrape our first page:

.. code-block:: python

  from urlparse import urljoin

  @scraper.task
  def scrape_index(url):
      doc = scraper.get(url).html()

      next_link = doc.find('.//a[@class="button next"]')
      if next_link is not None:
          # make an absolute url.
          next_url = urljoin(url, next_link.get('href'))
          scrape_index.queue(next_url)

  scrape_index.run('https://sfbay.craigslist.org/boo/')

This code will cycle through all the pages of listings, as long as
a *Next* link is present.

The key aspect of this snippet is the notion of a :py:class:`task
<scrapekit.tasks.Task>`. Each scrapekit scraper is broken up into
many small tasks, ideally one for fetching each web page.

Tasks are executed in parallel to speed up the scraper. To do that,
task functions aren't called directly, but by placing them on a
queue (see :py:func:`scrape_index.queue <scrapekit.tasks.Task.queue>`
above). Like normal functions, they can still receive arguments - 
in this case, the URL to be scraped.

At the end of the snippet, we're calling :py:func:`scrape_index.run
<scrapekit.tasks.Task.run>`. Unlike a simple queueing operation, this
will tell the scraper to queue a task and then wait for all tasks to
be executed.


Scraping details
----------------

Now that we have a basic task to scrape the index of listings, we
might want to download each listing's page and get some data from it. 
To do this, we can extend our previous script:

.. code-block:: python

  import scrapekit
  from urlparse import urljoin

  scraper = scrapekit.Scraper('craigslist-sf-boats')

  @scraper.task
  def scrape_listing(url):
      doc = scraper.get(url).html()
      print doc.find('.//h2[@class="postingtitle"]').text_content()


  @scraper.task
  def scrape_index(url):
      doc = scraper.get(url).html()

      for listing in doc.findall('.//a[@class="hdrlnk"]'):
          listing_url = urljoin(url, listing.get('href'))
          scrape_listing.queue(listing_url)

      next_link = doc.find('.//a[@class="button next"]')
      if next_link is not None:
          # make an absolute url.
          next_url = urljoin(url, next_link.get('href'))
          scrape_index.queue(next_url)

  scrape_index.run('https://sfbay.craigslist.org/boo/')

This basic scraper could be extended to extract more information from 
each listing page, and to save that information to a set of files or 
to a database.


Configuring the scraper
-----------------------

As you may have noticed, Craigslist is sometimes a bit slow. You might
want to configure your scraper to use caching, or a different number 
of simultaneous threads to retrieve data. The simplest way to set up
caching is to set some environment variables:

.. code-block:: bash

  $ export SCRAPEKIT_CACHE_POLICY="http"
  $ export SCRAPEKIT_DATA_PATH="data"
  $ export SCRAPEKIT_THREADS=10

This will instruct scrapekit to cache requests according to the rules
of HTTP (using headers like ``Cache-Control`` to determine what to cache
and for how long), and to save downloaded data in a directory called
``data`` in the current working path. We've also instructed the tool to
use 10 threads when scraping data.

If you wanto to make these decisions at run-time, you could also pass
them into the constructor of your :py:class:`Scraper
<scrapekit.core.Scraper>`:

.. code-block:: python

  import scrapekit

  config = {
    'threads': 10,
    'cache_policy': 'http',
    'data_path': 'data'
  }
  scraper = scrapekit.Scraper('demo', config=config)

For details on all available settings and their meaning, check out the 
configuration documentation.

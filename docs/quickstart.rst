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

The key aspect of this snippet is the notion of a ``task``. Each 
scrapekit scraper is broken up into many small tasks, ideally one
for fetching each web page.

Tasks are executed in parallel to speed up the scraper. For that
purpose, task functions aren't called directly, but by placing
them on a queue (see ``scrape_index.queue`` above). Like normal 
functions, they can still receive arguments - in this case, the URL
to be scraped.

At the end of the snippet, we're calling ``scrape_index.run``. Unlike
a simple queueing operation, this will tell the scraper to queue a 
task and then wait for all tasks to be executed.



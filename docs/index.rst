.. scrapekit documentation master file, created by
   sphinx-quickstart on Wed Aug  6 15:12:35 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

scrapekit: get the data you need, fast.
=======================================

.. toctree::
   :hidden:

Many web sites expose a great amount of data, and scraping it can help you build
useful tools, services and analysis on top of that data. This can often be done
with a simple Python script, using few external libraries.

As your script grows, however, you will want to add more advanced features, such
as **caching** of the downloaded pages, **multi-threading** to fetch many pieces
of content at once, and **logging** to get a clear sense of which data failed to
parse.

Scrapekit provides a set of useful tools for these that help with these tasks, 
while also offering you simple ways to structure your scraper. This helps you to
produce **fast, reliable and structured scraper scripts**.

Example
-------

Below is a simple scraper for postings on Craigslist. This will use
multiple threads and request caching by default.

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

  scrape_index.run('https://sfbay.craigslist.org/boo/')


Contents
--------

.. toctree::
   :maxdepth: 2

   install
   quickstart
   tasks
   utils
   config
   api

Contributors
------------

``scrapekit`` is written and maintained by `Friedrich Lindenberg
<https://github.com/pudo>`_. It was developed as an outcome of scraping projects
for the `African Network of Centers for Investigative Reporting (ANCIR)
<http://investigativecenters.org>`_, supported by a `Knight International
Journalism Fellowship <http://icfj.org/knight>`_ from the `International
Center for Journalists (ICFJ) <http://icfj.org>`_.




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


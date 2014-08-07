
What should a typical session look like?

## Fetching stuff from the web

```python
from scrapekit import config, http

config.cache_forever = True
config.cache_dir = '/tmp'

res = http.get('http://databin.pudo.org/t/b2d9cf')
```

Good enough. This should retain a cache of the data locally, and do
retrieval.

Other concerns:

* Rate limiting
* User agent hiding, and very explicit UAs.

## Parallel processing

Next up: threading. Basically a really light-weight, in-process
version of celery? Perhaps with an option to go for the real thing
when needed?

```python
from scrapekit import processing

@processing.task
def scrape_page(url):
  pass

scrape_page.queue(url)
processing.init(num_threads=20)
```

Alternatively, this could support a system of pipelines like this:

```python
from scrapekit import processing

@processing.task
def scrape_index():
  for i in xrange(1000):
    yield 'http://example.com/%d' % i

@processing.task
def scrape_page(url):
  pass

pipeline = scrape_index.pipeline()
pipeline = pipeline.chain(scrape_page)
pipeline.run(num_threads=20)
```

## Logging

What would really good logging for scrapers look like?

* Includes context, such as the URL currently being processed
* All the trivial stuff (HTTP issues, HTML/XML parsing) is handled
* Logs go to a CSV file or database? Something that allows
  systematic analysis.
* Does this actually generate nice-to-look at HTML?
* Set up sensible defaults for Requests logging

## Audits

Audits are parts of a pipeline that validate the generated data against a
pre-defined schema. This could be used to make sure the data meets 
certain expectations.

## Other functionality

What else is repeated all over scrapers?

* Text cleaning (remove multiple spaces, normalize).
* Currency conversion and deflation
* Geocoding of addresses


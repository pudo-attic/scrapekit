import os
import math
import platform
import pkg_resources
from datetime import datetime
from collections import namedtuple

from jinja2 import Environment, PackageLoader


PAGE_SIZE = 15
RANGE = 3
url = namedtuple('url', ['idx', 'rel', 'abs'])


def datetimeformat(value):
    outfmt = '%b %d, %Y, %H:%M'
    if value is None:
        return 'no date'
    if not isinstance(value, datetime):
        value = datetime.strptime(value, '%Y-%m-%dT%H:%M')
    return value.strftime(outfmt)


def render(scraper, dest_file, template, **kwargs):
    reports_path = scraper.config.reports_path
    if reports_path is None:
        reports_path = os.path.join(scraper.config.data_path, 'reports')
    dest_file = os.path.join(reports_path, dest_file)
    dest_path = os.path.dirname(dest_file)
    try:
        os.makedirs(dest_path)
    except:
        pass

    loader = PackageLoader('scrapekit', 'templates')
    env = Environment(loader=loader)
    env.filters['dateformat'] = datetimeformat
    template = env.get_template(template)
    kwargs['version'] = pkg_resources.require("scrapekit")[0].version
    kwargs['python'] = platform.python_version()
    kwargs['hostname'] = platform.uname()[1]
    with open(dest_file, 'w') as fh:
        kwargs['scraper'] = scraper
        fh.write(template.render(**kwargs))
    return dest_file


def paginate(scraper, elements, basename, template, **kwargs):
    basedir = os.path.dirname(basename)
    basefile = os.path.basename(basename)
    pages = int(math.ceil(float(len(elements)) / PAGE_SIZE))

    urls = []
    for i in range(1, pages + 1):
        fn = basefile % '' if i == 1 else basefile % i
        urls.append(url(i, fn, os.path.join(basedir, fn)))

    link = None
    for page in reversed(urls):
        offset = (page.idx - 1) * PAGE_SIZE
        es = elements[offset:offset + PAGE_SIZE]

        low = page.idx - RANGE
        high = page.idx + RANGE

        if low < 1:
            low = 1
            high = min((2 * RANGE) + 1, pages)

        if high > pages:
            high = pages
            low = max(1, pages - (2 * RANGE) + 1)

        pager = {
            'total': len(elements),
            'page': page,
            'elements': es,
            'pages': urls[low - 1:high],
            'show': pages > 1,
            'prev': None if page.idx == 1 else urls[page.idx - 2],
            'next': None if page.idx == len(urls) else urls[page.idx]
        }
        link = render(scraper, page.abs, template, pager=pager,
                      **kwargs)
    return link

import os
import math
import platform
import pkg_resources
from collections import namedtuple

from jinja2 import Environment, PackageLoader


PAGE_SIZE = 20
RANGE = 3
url = namedtuple('url', ['idx', 'rel', 'abs'])


def render(scraper, dest_file, template, **kwargs):
    dest_file = os.path.join(scraper.config.reports_path, dest_file)
    dest_path = os.path.dirname(dest_file)
    if not os.path.isdir(dest_path):
        os.makedirs(dest_path)

    loader = PackageLoader('scrapekit', 'templates')
    env = Environment(loader=loader)
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
    pages = int(math.ceil(float(len(elements))/PAGE_SIZE))

    urls = []
    for i in range(1, pages + 1):
        fn = basefile % '' if i == 1 else basefile % i
        urls.append(url(i, fn, os.path.join(basedir, fn)))

    link = None
    for page in reversed(urls):
        offset = (page.idx - 1) * PAGE_SIZE
        es = elements[offset:offset+PAGE_SIZE]

        low = page.idx - RANGE
        high = page.idx + RANGE

        if low < 1:
            low = 1
            high = min((2*RANGE)+1, pages)

        if high > pages:
            high = pages
            low = max(1, pages - (2*RANGE)+1)

        pager = {
            'page': page,
            'elements': es,
            'pages': urls[low-1:high],
            'prev': None if page.idx == 1 else urls[page.idx-2],
            'next': None if page.idx == len(urls) else urls[page.idx]
        }
        link = render(scraper, page.abs, template, pager=pager,
                      **kwargs)
    return link

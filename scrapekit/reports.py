import os
import json
from collections import defaultdict
from pprint import pprint

from jinja2 import Environment, PackageLoader

from scrapekit.logs import log_path


def log_parse(scraper):
    path = log_path(scraper)
    with open(path, 'r') as fh:
        for line in fh:
            yield json.loads(line)


def render_file(scraper, dest_file, template, **kwargs):
    dest_file = os.path.join(scraper.config.reports_path, dest_file)
    dest_path = os.path.dirname(dest_file)
    if not os.path.isdir(dest_path):
        os.makedirs(dest_path)

    loader = PackageLoader('scrapekit', 'templates')
    env = Environment(loader=loader)
    template = env.get_template(template)
    with open(dest_file, 'w') as fh:
        kwargs['scraper'] = scraper
        fh.write(template.render(**kwargs))
    return dest_file


def generate_report(scraper):
    runs = {}
    for item in log_parse(scraper):
        if item.get('scraperName') != scraper.name:
            continue
        scraper_id = item.get('scraperId')
        if scraper_id not in runs:
            runs[scraper_id] = {
                'id': scraper_id,
                'logs': defaultdict(int),
                'tasks': set(),
                'messages': 0,
                'link': os.path.join('runs', scraper_id, 'index.html'),
                'start_time': item.get('scraperStartTime')
            }
        runs[scraper_id]['logs'][item.get('levelname')] += 1
        runs[scraper_id]['messages'] += 1
        if item.get('taskId'):
            runs[scraper_id]['tasks'].add(item.get('taskId'))

    runs = sorted(runs.values(), key=lambda r: r.get('start_time'),
                  reverse=True)
    index_file = render_file(scraper, 'index.html', 'index.html',
                             runs=runs)

    return index_file

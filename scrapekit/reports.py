import os
import json
from collections import defaultdict
from pprint import pprint


from scrapekit.logs import log_path
from scrapekit.render import render, paginate


def log_parse(scraper):
    path = log_path(scraper)
    with open(path, 'r') as fh:
        for line in fh:
            data = json.loads(line)
            if data.get('scraperName') != scraper.name:
                continue
            yield data


def generate_report(scraper):
    runs = {}
    for item in log_parse(scraper):
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
    index_file = paginate(scraper, runs, 'index%s.html', 'index.html')
    return index_file

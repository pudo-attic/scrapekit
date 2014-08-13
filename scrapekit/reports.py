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
    for run in runs:
        generate_run(scraper, run)
    return index_file


def generate_run(scraper, run):
    prefix = os.path.join('runs', run['id'])
    tasks = {}
    for item in log_parse(scraper):
        task_name = item.get('taskName', 'no_task')
        if task_name not in tasks:
            tasks[task_name] = {
                'name': task_name,
                'logs': defaultdict(int),
                'tasks': set(),
                'messages': 0,
                'link': os.path.join(prefix, '%s.html' % task_name),
            }
        tasks[task_name]['logs'][item.get('levelname')] += 1
        tasks[task_name]['messages'] += 1
        if item.get('taskId'):
            tasks[task_name]['tasks'].add(item.get('taskId'))

    tasks = sorted(tasks.values(), key=lambda r: len(r.get('tasks')),
                  reverse=True)
    paginate(scraper, tasks, os.path.join(prefix, 'index%s.html'),
             'run.html')

from os import path

from scrapekit.reporting import db
from scrapekit.reporting import render


RUNS_QUERY = """
    SELECT scraperId, scraperStartTime, levelname, COUNT(rowid) as messages,
        COUNT(DISTINCT taskId) AS tasks
    FROM log
    GROUP BY scraperId, scraperStartTime, levelname
    ORDER BY scraperStartTime DESC
"""

TASKS_QUERY = """
    SELECT scraperId, scraperStartTime, levelname, taskName,
        COUNT(rowid) as messages, COUNT(DISTINCT taskId) AS tasks
    FROM log
    GROUP BY scraperId, scraperStartTime, levelname, taskName
    ORDER BY scraperId DESC, taskName DESC
"""

TASK_RUNS_QUERY = """
    SELECT taskId, scraperId, taskName, asctime, levelname,
        COUNT(rowid) as messages,
        COUNT(DISTINCT taskId) AS tasks
    FROM log
    WHERE scraperId = :scraperId AND taskName = :taskName
    GROUP BY taskId, scraperId, taskName, asctime, levelname
    ORDER BY messages DESC
"""

TASK_RUNS_QUERY_NULL = """
    SELECT taskId, scraperId, taskName, asctime, levelname,
        COUNT(rowid) as messages,
        COUNT(DISTINCT taskId) AS tasks
    FROM log
    WHERE scraperId = :scraperId AND taskName IS NULL
    GROUP BY taskId, scraperId, taskName, asctime, levelname
    ORDER BY messages DESC
"""

TASK_RUNS_LIST = """
SELECT DISTINCT scraperId, taskName FROM log ORDER BY asctime DESC
"""


def aggregate_loglevels(sql, keys, **kwargs):
    data, key = {}, None
    for row in db.query(sql, **kwargs):
        row_key = map(lambda k: row[k], keys)
        if key != row_key:
            if key is not None:
                yield data
            data = row
            key = row_key
        else:
            data['messages'] += row['messages']
            data['tasks'] += row['tasks']
        data[row['levelname']] = row['messages']
    if key is not None:
        yield data


def generate(scraper):
    db.load(scraper)
    runs = list(aggregate_loglevels(RUNS_QUERY, ('scraperId',)))
    tasks = list(aggregate_loglevels(TASKS_QUERY, ('scraperId', 'taskName')))
    index_file = render.paginate(scraper, runs, 'index%s.html', 'index.html',
                                 tasks=tasks)

    for task_run in db.query(TASK_RUNS_LIST):
        task = task_run.get('taskName') or render.PADDING
        file_name = 'tasks/%s/%s%%s.html' % (task, task_run.get('scraperId'))
        if path.exists(path.join(path.dirname(index_file), file_name % '')):
            continue
        if task_run.get('taskName') is None:
            runs = aggregate_loglevels(TASK_RUNS_QUERY_NULL, ('taskId',),
                                       scraperId=task_run.get('scraperId'))
        else:
            runs = aggregate_loglevels(TASK_RUNS_QUERY, ('taskId',),
                                       scraperId=task_run.get('scraperId'),
                                       taskName=task_run.get('taskName'))
        render.paginate(scraper, list(runs), file_name, 'run.html')

    return index_file

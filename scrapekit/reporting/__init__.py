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


def sort_aggregates(rows):
    rows = list(rows)

    def key(row):
        return row.get('ERROR', 0) * (len(rows) * 2) + \
            row.get('WARN', 0) * len(rows) + \
            row.get('INFO', 0) * 2 + \
            row.get('DEBUG', 0)
    return sorted(rows, key=key)


def all_task_runs(scraper, keys=('scraperId', 'taskId')):
    by_task = {}
    for row in db.log_parse(scraper):
        asctime = row.get('asctime')
        row['ts'] = '-' if asctime is None else asctime.rsplit(' ')[-1]
        row_key = tuple(map(lambda k: row.get(k), keys))
        if row_key not in by_task:
            by_task[row_key] = [row]
        else:
            by_task[row_key].append(row)
    return by_task


def generate(scraper):
    db.load(scraper)
    runs = list(aggregate_loglevels(RUNS_QUERY, ('scraperId',)))
    tasks = list(aggregate_loglevels(TASKS_QUERY, ('scraperId', 'taskName')))
    index_file = render.paginate(scraper, runs, 'index%s.html', 'index.html',
                                 tasks=tasks)

    for task_run in db.query(TASK_RUNS_LIST):
        task = task_run.get('taskName') or render.PADDING
        file_name = '%s/%s/index%%s.html' % (task, task_run.get('scraperId'))
        if path.exists(path.join(path.dirname(index_file), file_name % '')):
            continue
        if task_run.get('taskName') is None:
            runs = aggregate_loglevels(TASK_RUNS_QUERY_NULL, ('taskId',),
                                       scraperId=task_run.get('scraperId'))
        else:
            runs = aggregate_loglevels(TASK_RUNS_QUERY, ('taskId',),
                                       scraperId=task_run.get('scraperId'),
                                       taskName=task_run.get('taskName'))
        runs = sort_aggregates(runs)
        render.paginate(scraper, runs, file_name, 'task_run_list.html',
                        taskName=task)

    for (scraperId, taskId), rows in all_task_runs(scraper).items():
        taskName = rows[0].get('taskName')
        file_name = (taskName or render.PADDING,
                     scraperId or render.PADDING,
                     taskId or render.PADDING)
        file_name = '%s/%s/%s%%s.html' % file_name
        if path.exists(path.join(path.dirname(index_file), file_name % '')):
            continue
        render.paginate(scraper, rows, file_name, 'task_run_item.html',
                        scraperId=scraperId, taskId=taskId, taskName=taskName)

    return index_file

from scrapekit.reports import db
from scrapekit.reports import render


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


def aggregate_loglevels(sql, keys):
    data, key = {}, None
    for row in db.query(sql):
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
    return index_file

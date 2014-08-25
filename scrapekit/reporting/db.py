import json
import sqlite3

from scrapekit.logs import log_path


conn = sqlite3.connect(':memory:')
#conn = sqlite3.connect('foo.db')


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def log_parse(scraper):
    path = log_path(scraper)
    with open(path, 'r') as fh:
        for line in fh:
            data = json.loads(line)
            if data.get('scraperName') != scraper.name:
                continue
            yield data


def load(scraper):
    conn.row_factory = dict_factory
    conn.execute("""CREATE TABLE log (scraperId text, taskName text,
        scraperStartTime datetime, levelname text, taskId text)""")
    conn.commit()
    for data in log_parse(scraper):
        conn.execute("""INSERT INTO log (scraperId, taskName,
            scraperStartTime, levelname, taskId) VALUES
            (?, ?, ?, ?, ?)""",
            (data.get('scraperId'), data.get('taskName'),
             data.get('scraperStartTime'), data.get('levelname'),
             data.get('taskId')))
    conn.commit()
    return conn


def query(sql, **kwargs):
    rp = conn.execute(sql, kwargs)
    for row in rp.fetchall():
        yield row

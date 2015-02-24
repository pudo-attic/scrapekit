import os
import atexit
from uuid import uuid4
from datetime import datetime
from threading import local
import threading
import json
import hashlib

from scrapekit.config import Config
from scrapekit.tasks import TaskManager, Task
from scrapekit.http import make_session
from scrapekit.logs import make_logger
from scrapekit import reporting

import dataset


class DBLock(object):
    def __init__(self, lock, db):
        self.lock = lock
        self.db = db

    def __enter__(self):
        self.lock.acquire()
        self.conn = dataset.connect(self.db)
        self.conn.__enter__()
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.__exit__(exc_type, exc_value, traceback)
        self.lock.release()


class Scraper(object):
    """ Scraper application object which handles resource management
    for a variety of related functions. """

    def __init__(self, name, config=None, report=False):
        self.name = name
        self.id = uuid4()
        self.start_time = datetime.utcnow()
        self.config = Config(self, config)
        try:
            os.makedirs(self.config.data_path)
        except:
            pass
        self._task_manager = None
        self.task_ctx = local()
        self.log = make_logger(self)

        self.db_lock = threading.Lock()

        self.session = self.Session()
        if report:
            atexit.register(self.report)

    def get_db(self):
        db_path = 'sqlite:///%s' % os.path.join(self.config.data_path, 'tasks.db')
        return DBLock(self.db_lock, db_path)

    @property
    def task_manager(self):
        if self._task_manager is None:
            self._task_manager = \
                TaskManager(threads=self.config.threads)
        return self._task_manager

    def task(self, fn):
        """ Decorate a function as a task in the scraper framework.
        This will enable the function to be queued and executed in
        a separate thread, allowing for the execution of the scraper
        to be asynchronous.
        """
        return Task(self, fn)

    def write_result(self, *args):
        with self.get_db() as db:
            db['results'].upsert(*args)

    def store_tasks(self, name, args_iter):
        self.log.info('Storing tasks for %s', name)
        generator = self.get_task_generator(name, args_iter)
        with self.get_db() as db:
            item = generator.next()
            res = db['tasks'].find_one(task_id=item['task_id'])
            if res is not None:
                self.log.info('Found first task, skipping %s', name)
                return
            # Add first item to create structure
            db['tasks'].upsert(item, ['task_id'])

        with self.get_db() as db:
            # Bulk insert rest
            table = db['tasks'].table
            table.insert().execute(list(generator))

    def get_task_generator(self, name, args_iter):
        for args_kwargs in args_iter:
            if isinstance(args_kwargs, tuple):
                if len(args_kwargs) == 2 and isinstance(args_kwargs[0], tuple):
                    args, kwargs = args_kwargs
                else:
                    args = args_kwargs
                    kwargs = {}
            else:
                args = (args_kwargs,)
                kwargs = {}
            task_id = self.get_task_id(name, args, kwargs)
            yield {
                'task_id': task_id,
                'name': name,
                'args': json.dumps(args),
                'kwargs': json.dumps(kwargs),
                'value': None,
                'exception': None
            }

    def get_task_id(self, name, args, kwargs):
        task_id = hashlib.md5()
        task_id.update(name)
        task_id.update(json.dumps(args))
        task_id.update(json.dumps(kwargs))
        return task_id.hexdigest()

    def process_tasks(self, task_name=None):
        self.log.info('Processing all tasks')

        filt = {'done': None}
        if task_name is not None:
            filt['name'] = task_name

        tasks = []
        with self.get_db() as db:
            for i, task in enumerate(db['tasks'].find(**filt)):
                tasks.append(task)

        for task in tasks:
            task_obj = Task(self, getattr(self, task['name']),
                            task_id=task['task_id'])
            args = json.loads(task['args'])
            kwargs = json.loads(task['kwargs'])
            task_obj.queue(*args, **kwargs)

        self.task_manager.wait()

    def Session(self):
        """ Create a pre-configured ``requests`` session instance
        that can be used to run HTTP requests. This instance will
        potentially be cached, or a stub, depending on the
        configuration of the scraper. """
        return make_session(self)

    def head(self, url, **kwargs):
        """ HTTP HEAD via ``requests``.

        See: http://docs.python-requests.org/en/latest/api/#requests.head
        """
        return self.Session().get(url, **kwargs)

    def get(self, url, **kwargs):
        """ HTTP GET via ``requests``.

        See: http://docs.python-requests.org/en/latest/api/#requests.get
        """
        return self.Session().get(url, **kwargs)

    def post(self, url, **kwargs):
        """ HTTP POST via ``requests``.

        See: http://docs.python-requests.org/en/latest/api/#requests.post
        """
        return self.Session().post(url, **kwargs)

    def put(self, url, **kwargs):
        """ HTTP PUT via ``requests``.

        See: http://docs.python-requests.org/en/latest/api/#requests.put
        """
        return self.Session().put(url, **kwargs)

    def report(self):
        """ Generate a static HTML report for the last runs of the
        scraper from its log file. """
        index_file = reporting.generate(self)
        print("Report available at: file://%s" % index_file)

    def __repr__(self):
        return '<Scraper(%s)>' % self.name

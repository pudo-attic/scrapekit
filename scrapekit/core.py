from uuid import uuid4
from datetime import datetime
from threading import local

from scrapekit.config import Config
from scrapekit.tasks import TaskManager, Task
from scrapekit.http import make_session
from scrapekit.logs import make_logger


class Scraper(object):
    """ Scraper application object which handles resource management
    for a variety of related functions. """

    def __init__(self, name, config=None):
        self.name = name
        self.id = uuid4()
        self.start_time = datetime.utcnow()
        self.config = Config(self, config)
        self._task_manager = None
        self.task_ctx = local()
        self.log = make_logger(self)
        self.log.info("Starting %s, %d threads.", self.name,
                      self.config.threads)

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

    def __repr__(self):
        return '<Scraper(%s)>' % self.name

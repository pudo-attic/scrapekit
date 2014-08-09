from scrapekit.config import Config
from scrapekit.tasks import TaskManager, Task


class Scraper(object):
    """ Scraper application object which handles resource management
    for a variety of related functions. """

    def __init__(self, name, config=None):
        self.name = name
        self.config = Config(self, config)
        self._task_manager = None

    @property
    def task_manager(self):
        if self._task_manager is None:
            self._task_manager = \
                TaskManager(threads=self.config.threads)
        return self._task_manager

    def task(self, fn):
        """ Decorate a function as a task in the scraper framework.
        """
        return Task(self, fn)

    def __repr__(self):
        return '<Scraper(%s)>' % self.name

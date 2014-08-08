"""
Task/processing tools.

This module holds a simple system for the multi-threaded execution of
scraper code. This can be used, for example, to split a scraper into
several stages and to have multiple elements processed at the same
time.

The goal of this module is to handle simple multi-threaded scrapers,
while making it easy to upgrade to a queue-based setup using celery
later.
"""

from inspect import isgenerator
try:
    from queue import Queue
except ImportError:
    from Queue import Queue
from threading import Thread


class TaskManager(object):

    def __init__(self, threads=10, max_queue=200, daemon=True):
        """
        :param threads: The number of threads to be spawned. Values
            ranging from 5 to 40 have shown useful, based on the amount
            of I/O involved in each task.
        :param max_queue: How many queued items should be read from the
            generator and put on the queue before processing is halted
            to allow the processing to catch up.
        :param daemon: Mark the worker threads as daemons in the
            operating system, so that they will not be included in the
            number of application threads for this script.
        """
        self.num_threads = threads
        self.max_queue = max_queue
        self.daemon = daemon
        self.queue = None

    def _spawn(self):
        self.queue = Queue(maxsize=self.max_queue)
        for i in range(self.num_threads):
            t = Thread(target=self._consume)
            t.daemon = self.daemon
            t.start()

    def _consume(self):
        while True:
            try:
                task, args, kwargs = self.queue.get(True)
                task(*args, **kwargs)
            finally:
                self.queue.task_done()

    def put(self, task, args, kwargs):
        if self.queue is None:
            self._spawn()
        self.queue.put((task, args, kwargs))

    def wait(self):
        if self.queue is None:
            return
        self.queue.join()


class Task(object):

    _manager = TaskManager()

    def __init__(self, fn, threads=None, max_queue=None):
        self.fn = fn
        self._chained = []

    def __call__(self, *args, **kwargs):
        bind = lambda: self.fn(*args, **kwargs)
        # TODO: lots of exception handling etc.
        if len(self._chained):
            retval = bind()
            if isgenerator(retval):
                for item in retval:
                    self._notify(item)
            else:
                self._notify(retval)
        else:
            return bind()

    def queue(self, *args, **kwargs):
        """ Schedule a task for execution. """
        self._manager.put(self, args, kwargs)
        return self

    def wait(self):
        self._manager.wait()
        return self

    def _notify(self, value):
        for task in self._chained:
            task.queue(value)

    def chain(self, other_task):
        self._chained.append(other_task)
        return self

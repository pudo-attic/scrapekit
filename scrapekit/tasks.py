"""
This module holds a simple system for the multi-threaded execution of
scraper code. This can be used, for example, to split a scraper into
several stages and to have multiple elements processed at the same
time.

The goal of this module is to handle simple multi-threaded scrapers,
while making it easy to upgrade to a queue-based setup using celery
later.
"""

from uuid import uuid4
from time import sleep
try:
    from queue import Queue
except ImportError:
    from Queue import Queue
from threading import Thread


class TaskManager(object):
    """ The `TaskManager` is a singleton that manages the threads
    used to parallelize processing and the queue that manages the
    current set of prepared tasks. """

    def __init__(self, threads=10):
        """
        :param threads: The number of threads to be spawned. Values
            ranging from 5 to 40 have shown useful, based on the amount
            of I/O involved in each task.
        :param daemon: Mark the worker threads as daemons in the
            operating system, so that they will not be included in the
            number of application threads for this script.
        """
        self.num_threads = int(threads)
        self.queue = None

    def _spawn(self):
        """ Initialize the queue and the threads. """
        self.queue = Queue(maxsize=self.num_threads * 10)
        for i in range(self.num_threads):
            t = Thread(target=self._consume)
            t.daemon = True
            t.start()

    def _consume(self):
        """ Main loop for each thread, handles picking a task off the
        queue, processing it and notifying the queue that it is done.
        """
        while True:
            try:
                task, args, kwargs = self.queue.get(True)
                task(*args, **kwargs)
            finally:
                self.queue.task_done()

    def put(self, task, args, kwargs):
        """ Add a new item to the queue. An item is a task and the
        arguments needed to call it.

        Do not call this directly, use Task.queue/Task.run instead.
        """
        if self.queue is None:
            self._spawn()
        self.queue.put((task, args, kwargs))

    def wait(self):
        """ Wait for each item in the queue to be processed. If this
        is not called, the main thread will end immediately and none
        of the tasks assigned to the threads would be executed. """
        if self.queue is None:
            return

        self.queue.join()


class ChainListener(object):

    def __init__(self, task):
        self.task = task

    def notify(self, value):
        self.task.queue(value)


class PipeListener(ChainListener):

    def notify(self, value):
        # TODO: if value is a generator, it will be exhausted.
        # Thus no branching or return value is available.
        # -> consider using itertools.tee.
        for value_item in value:
            self.task.queue(value_item)


class Task(object):
    """ A task is a decorator on a function which helps managing the
    execution of that function in a multi-threaded, queued context.

    After a task has been applied to a function, it can either be used
    in the normal way (by calling it directly), through a simple queue
    (using the `queue` method), or in pipeline mode (using `chain`,
    `pipe` and `run`).
    """

    def __init__(self, scraper, fn, task_id=None):
        self.scraper = scraper
        self.fn = fn
        self.task_id = task_id
        self._listeners = []
        self._source = None

    def __call__(self, *args, **kwargs):
        """ Execute the wrapped function. This will either call it in
        normal mode (returning the return value), or notify any
        pipeline listeners that have been associated with this task.
        """
        self.scraper.task_ctx.name = self.fn.func_name
        self.scraper.task_ctx.id = self.task_id or uuid4()

        try:
            self.scraper.log.debug('Begin task', extra={
                'taskArgs': args,
                'taskKwargs': kwargs
                })
            value = self.fn(*args, **kwargs)
            for listener in self._listeners:
                listener.notify(value)
            return value
        except Exception, e:
            self.scraper.log.exception(e)
        finally:
            self.scraper.task_ctx.name = None
            self.scraper.task_ctx.id = None

    def queue(self, *args, **kwargs):
        """ Schedule a task for execution. The task call (and its
        arguments) will be placed on the queue and processed
        asynchronously. """
        self.scraper.task_manager.put(self, args, kwargs)
        return self

    def wait(self):
        """ Wait for task execution in the current queue to be
        complete (ie. the queue to be empty). If only `queue` is called
        without `wait`, no processing will occur. """
        self.scraper.task_manager.wait()
        return self

    def run(self, *args, **kwargs):
        """ Queue a first item to execute, then wait for the queue to
        be empty before returning. This should be the default way of
        starting any scraper.
        """
        if self._source is not None:
            return self._source.run(*args, **kwargs)
        else:
            self.queue(*args, **kwargs)
            return self.wait()

    def chain(self, other_task):
        """ Add a chain listener to the execution of this task. Whenever
        an item has been processed by the task, the registered listener
        task will be queued to be executed with the output of this task.

        Can also be written as::

            pipeline = task1 > task2
        """
        other_task._source = self
        self._listeners.append(ChainListener(other_task))
        return other_task

    def pipe(self, other_task):
        """ Add a pipe listener to the execution of this task. The
        output of this task is required to be an iterable. Each item in
        the iterable will be queued as the sole argument to an execution
        of the listener task.

        Can also be written as::

            pipeline = task1 | task2
        """
        other_task._source = self
        self._listeners.append(PipeListener(other_task))
        return other_task

    def __gt__(self, other_task):
        return self.chain(other_task)

    def __or__(self, other_task):
        return self.pipe(other_task)

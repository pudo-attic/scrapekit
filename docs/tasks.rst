Using tasks
===========

Tasks are used by scrapekit to break up a complex script into small
units of work which can be executed asynchronously. When needed,
they can also be composed in a variety of ways to generate complex
data processing pipelines.


Explicit queueing
-----------------

The most simple way of using tasks is by explicitly queueing them.
Here's an example of a task queueing another task a few times:

.. code-block:: python

  import scrapekit

  scraper = scrapekit.Scraper('test')

  @scraper.task
  def each_item(item):
      print item

  @scraper.task
  def generate_work():
      for i in xrange(100):
          each_item.queue(i)

  if __name__ == '__main__':
      generate_work.queue().wait()


As you can see, ``generate_work`` will call ``each_item`` for each
item in the range. Since the items are processed asynchronously, 
the printed output will not be in order, but slightly mixed up.

You can also see that on the last line, we're queueing the 
``generate_work`` task itself, and then instructing scrapekit to 
wait for the completion of all tasks. Since the double call is a
bit awkward, there's a helper function to make both calls at once:

.. code-block:: python

  if __name__ == '__main__':
      generate_work.run()


Task chaining and piping
------------------------

As an alternative to these explicit instructions to queue, you can 
also use a more pythonic model to declare processing pipelines. A 
processing pipeline connects tasks by feeding the output of one task
to another task.

To connect tasks, there are two methods: chaining and piping. Chaining
will just take the return value of one task, and queue another task
to process it. Piping, on the other hand, will expect the return value
of the first task to be an iterable, or for the task itself to be a 
generator. It will then initiate the next task for each item in the 
sequence.

Let's assume we have these functions defined:

.. code-block:: python

  import scrapekit

  scraper = scrapekit.Scraper('test')

  @scraper.task
  def consume_item(item):
      print item
  
  @scraper.task
  def process_item(item):
      return item ** 3

  @scraper.task
  def generate_items():
      for i in xrange(100):
          yield i


The simplest link we could do would be this simple chaining:

.. code-block:: python

  pipline = process_item > consume_item
  pipeline.run(5)

This linked ``process_item`` to ``consume_item``. Similarly, we could
use a very simple pipe:

.. code-block:: python

  pipline = generate_items | consume_item
  pipeline.run()

Finally, we can link all of the functions together:

.. code-block:: python

  pipline = generate_items | process_item > consume_item
  pipeline.run()


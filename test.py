from scrapekit.work import Task


@Task
def fun(a, b):
    print (a, b, a+b)
    return a + b

#print fun.queue(2, 3).wait()
#print fun(2, 3)


@Task
def funSource():
    for i in xrange(100):
        yield i

@Task
def funSink(i):
    print i ** 3


pipeline = funSource > funSink
pipeline.run()

#funSource.chain(funSink).run()
#funSource.queue().wait()

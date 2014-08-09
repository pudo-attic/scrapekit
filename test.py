from scrapekit import task


@task
def fun(a, b):
    print (a, b, a+b)
    return a + b

#print fun.queue(2, 3).wait()
#print fun(2, 3)


@task
def funSource():
    for i in xrange(100):
        yield i

@task
def funModifier(i):
    return i + 0.1

@task
def funSink(i):
    print i ** 3


pipeline = funSource | funModifier > funSink
pipeline.run()

#funSource.chain(funSink).run()
#funSource.queue().wait()

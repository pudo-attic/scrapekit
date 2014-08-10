from scrapekit import Scraper

scraper = Scraper('test')

@scraper.task
def fun(a, b):
    print (a, b, a+b)
    return a + b

#print fun.queue(2, 3).wait()
#print fun(2, 3)


@scraper.task
def funSource():
    for i in xrange(100):
        yield i

@scraper.task
def funModifier(i):
    return i + 0.1

@scraper.task
def funSink(i):
    print i ** 3


#pipeline = funSource | funModifier > funSink
#pipeline.run()

#funSource.chain(funSink).run()
#funSource.queue().wait()



@scraper.task
def scrape_index():
    url = 'https://sfbay.craigslist.org/boo/'
    session = scraper.Session()
    res = session.get(url)
    print res


scrape_index.run()


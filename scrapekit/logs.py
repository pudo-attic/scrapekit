import os
import logging

import jsonlogger


class TaskAdapter(logging.LoggerAdapter):
    """ Enhance any log messages with extra information about the
    current context of the scraper. """

    def __init__(self, logger, scraper):
        super(TaskAdapter, self).__init__(logger, {})
        self.scraper = scraper

    def process(self, msg, kwargs):
        extra = kwargs.get('extra', {})
        extra['scraperName'] = self.scraper.name
        extra['scraperId'] = self.scraper.id
        if hasattr(self.scraper.task_ctx, 'name'):
            extra['taskName'] = self.scraper.task_ctx.name
        if hasattr(self.scraper.task_ctx, 'id'):
            extra['taskId'] = self.scraper.task_ctx.id
        extra['scraperStartTime'] = self.scraper.start_time
        kwargs['extra'] = extra
        return (msg, kwargs)


def make_json_format():
    supported_keys = ['asctime', 'created', 'filename', 'funcName',
                      'levelname', 'levelno', 'lineno', 'module',
                      'msecs', 'message', 'name', 'pathname',
                      'process', 'processName', 'relativeCreated',
                      'thread', 'threadName']
    log_format = lambda x: ['%({0:s})'.format(i) for i in x]
    return ' '.join(log_format(supported_keys))


def make_logger(scraper):
    """ Create two log handlers, one to output info-level ouput to the
    console, the other to store all logging in a JSON file which will
    later be used to generate reports. """

    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)

    json_path = os.path.join(scraper.config.data_path,
                             '%s.jsonlog' % scraper.name)
    json_handler = logging.FileHandler(json_path)
    json_handler.setLevel(logging.DEBUG)
    json_formatter = jsonlogger.JsonFormatter(make_json_format())
    json_handler.setFormatter(json_formatter)
    logger.addHandler(json_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    fmt = '%(name)s [%(asctime)s]: %(levelname)-8s %(message)s'
    formatter = logging.Formatter(fmt)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger = logging.getLogger(scraper.name)
    logger = TaskAdapter(logger, scraper)
    return logger

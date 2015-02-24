import os
import multiprocessing
from ConfigParser import SafeConfigParser


class Config(object):
    """ An object to load and represent the configuration of the current
    scraper. This loads scraper configuration from the environment and a
    per-user configuration file (``~/.scraperkit.ini``). """

    def __init__(self, scraper, config):
        self.scraper = scraper
        self.config = self._get_defaults()
        self.config = self._get_file(self.config)
        self.config = self._get_env(self.config)
        if config is not None:
            self.config.update(config)

    def _get_defaults(self):
        name = self.scraper.name
        return {
            'cache_policy': 'http',
            'threads': multiprocessing.cpu_count() * 2,
            'data_path': os.path.join(os.getcwd(), 'data', name),
            'reports_path': None
        }

    def _get_env(self, config):
        """ Read environment variables based on the settings defined in
        the defaults. These are expected to be upper-case versions of
        the actual setting names, prefixed by ``SCRAPEKIT_``. """
        for option, value in config.items():
            env_name = 'SCRAPEKIT_%s' % option.upper()
            value = os.environ.get(env_name, value)
            config[option] = value
        return config

    def _get_file(self, config):
        """ Read a per-user .ini file, which is expected to have either
        a ``[scraperkit]`` or a ``[$SCRAPER_NAME]`` section. """
        config_file = SafeConfigParser()
        config_file.read([os.path.expanduser('~/.scrapekit.ini')])
        if config_file.has_section('scrapekit'):
            config.update(dict(config_file.items('scrapekit')))
        if config_file.has_section(self.scraper.name):
            config.update(dict(config_file.items(self.scraper.name)))
        return config

    def items(self):
        return self.config.items()

    def __getattr__(self, name):
        if name != 'config' and name in self.config:
            return self.config.get(name)
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return None

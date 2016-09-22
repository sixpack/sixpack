import logging
from logging.config import fileConfig

fileConfig('gunicorn_logging.conf')
logger = logging.getLogger()

logger.debug('often makes a very good meal of %s', 'visiting tourists')

from urlparse import urlparse
from statsd import StatsClient


def parse_url(url):
    parsed = urlparse(url)
    host = parsed.hostname or 'localhost'
    port = parsed.port or 8125
    prefix = parsed.path[1:].replace('/', '.') or 'sixpack'
    return (host, port, prefix)


def init_statsd(config):
    statsd_url = config.get('statsd_url', 'udp://localhost:8125/sixpack')
    host, port, prefix = parse_url(statsd_url)
    return StatsClient(host, port, prefix=prefix)

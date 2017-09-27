import yaml
import os

from utils import to_bool

config_path = os.environ.get('SIXPACK_CONFIG', None)
if config_path:
    try:
        CONFIG = yaml.safe_load(open(config_path, 'r'))
    except IOError:
        raise RuntimeError(
            'SIXPACK_CONFIG - {0} - is an invalid path'.format(config_path))
    except yaml.YAMLError, exc:
        raise RuntimeError('Error in configuration file: {0}'.format(str(exc)))
else:
    CONFIG = {
        'enabled': to_bool(os.environ.get('SIXPACK_CONFIG_ENABLED', 'True')),
        'redis_port': int(os.environ.get('SIXPACK_CONFIG_REDIS_PORT', '6379')),
        'redis_host': os.environ.get('SIXPACK_CONFIG_REDIS_HOST', "localhost"),
        'redis_password': os.environ.get('SIXPACK_CONFIG_REDIS_PASSWORD', None),
        'redis_prefix': os.environ.get('SIXPACK_CONFIG_REDIS_PREFIX', "sxp"),
        'redis_socket_timeout': os.environ.get('SIXPACK_CONFIG_REDIS_SOCKET_TIMEOUT', None),
        'redis_sentinel_service_name': os.environ.get('SIXPACK_CONFIG_REDIS_SENTINEL_SERVICE_NAME', None),
        'redis_max_connections': int(os.environ.get('SIXPACK_CONFIG_REDIS_MAX_CONNECTIONS', '0')),
        'redis_db': int(os.environ.get('SIXPACK_CONFIG_REDIS_DB', '15')),
        'robot_regex': os.environ.get('SIXPACK_CONFIG_ROBOT_REGEX', "$^|trivial|facebook|MetaURI|butterfly|google|"
                                                                    "amazon|goldfire|sleuth|xenu|msnbot|SiteUptime|"
                                                                    "Slurp|WordPress|ZIBB|ZyBorg|pingdom|bot|yahoo|"
                                                                    "slurp|java|fetch|spider|url|crawl|oneriot|abby|"
                                                                    "commentreader|twiceler"),
        'ignored_ip_addresses': os.environ.get('SIXPACK_CONFIG_IGNORE_IPS', "").split(","),
        'asset_path': os.environ.get('SIXPACK_CONFIG_ASSET_PATH', "gen"),
        'secret_key': os.environ.get('SIXPACK_CONFIG_SECRET', 'temp'),
        'csrf_disable': to_bool(os.environ.get('SIXPACK_CONFIG_CSRF_DISABLE', 'False')),
        'metrics': to_bool(os.environ.get('SIXPACK_METRICS', 'False')),
        'statsd_url': os.environ.get('STATSD_URL', 'udp://localhost:8125/sixpack'),
        'proxy_fix': to_bool(os.environ.get('SIXPACK_PROXY_FIX', 'False')),
        'cors_origin': os.environ.get("SIXPACK_CORS_ORIGIN", "*"),
        'cors_headers': os.environ.get("SIXPACK_CORS_HEADERS", "Origin, ..."),
        'cors_credentials': os.environ.get("SIXPACK_CORS_CREDENTIALS", "true"),
        'cors_methods': os.environ.get("SIXPACK_CORS_METHODS", "GET"),
        'cors_expose_headers': os.environ.get("SIXPACK_CORS_EXPOSE_HEADERS", "..."),
    }

    if 'SIXPACK_CONFIG_REDIS_SENTINELS' in os.environ:
        sentinels = []
        for sentinel in os.environ['SIXPACK_CONFIG_REDIS_SENTINELS'].split(","):
            server, port = sentinel.split(":")
            sentinels.append([server, int(port)])
        CONFIG['redis_sentinels'] = sentinels

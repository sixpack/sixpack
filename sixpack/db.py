import redis
from redis.connection import PythonParser

from config import CONFIG as cfg

# Because of a bug (https://github.com/andymccurdy/redis-py/issues/318) with
# script reloading in `redis-py, we need to force the `PythonParser` to prevent
# sixpack from crashing if redis restarts (or scripts are flushed).
if cfg.get('redis_sentinels'):
    from redis.sentinel import Sentinel, SentinelConnectionPool
    service_name = cfg.get('redis_sentinel_service_name')
    sentinel = Sentinel(sentinels=cfg.get('redis_sentinels'),
                        password=cfg.get('redis_password', None),
                        socket_timeout=cfg.get('redis_socket_timeout'))
    pool = SentinelConnectionPool(service_name, sentinel,
                                db=cfg.get('redis_db'),
                                max_connections=cfg.get('redis_max_connections'),
                                parser_class=PythonParser)
else:
    from redis.connection import ConnectionPool
    pool = ConnectionPool(host=cfg.get('redis_host'),
                        port=cfg.get('redis_port'),
                        password=cfg.get('redis_password', None),
                        db=cfg.get('redis_db'),
                        max_connections=cfg.get('redis_max_connections'),
                        parser_class=PythonParser)

REDIS = redis.StrictRedis(connection_pool=pool)
DEFAULT_PREFIX = cfg.get('redis_prefix')


def _key(k):
    return "{0}:{1}".format(DEFAULT_PREFIX, k)


monotonic_zadd = REDIS.register_script("""
    local sequential_id = redis.call('zscore', KEYS[1], ARGV[1])
    if not sequential_id then
        sequential_id = redis.call('zcard', KEYS[1])
        redis.call('zadd', KEYS[1], sequential_id, ARGV[1])
    end
    return sequential_id
""")


def sequential_id(k, identifier):
    """Map an arbitrary string identifier to a set of sequential ids"""
    key = _key(k)
    return int(monotonic_zadd(keys=[key], args=[identifier]))


msetbit = REDIS.register_script("""
    for index, value in ipairs(KEYS) do
        redis.call('setbit', value, ARGV[(index - 1) * 2 + 1], ARGV[(index - 1) * 2 + 2])
    end
    return redis.status_reply('ok')
""")


first_key_with_bit_set = REDIS.register_script("""
    for index, value in ipairs(KEYS) do
        local bit = redis.call('getbit', value, ARGV[1])
        if bit == 1 then
             return value
        end
    end
    return false
""")

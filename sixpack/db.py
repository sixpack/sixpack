from datetime import datetime
import redis

REDIS = redis.StrictRedis(host='localhost', port=6379, db=0)

DEFAULT_PREFIX = "sixpack"

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
def record_participation(_id, test, variation):
    """Record a user's participation in a test along with a given variation"""
    date = datetime.now()

    # TODO: Replace all %s % with .format()
    keys = [
        _key("participation:{0}".format(test)),
        _key("participation:{0}:{1}".format(test, variation)),
        _key("participation:{0}:{1}".format(test, date.strftime('%Y'))),
        _key("participation:{0}:{1}".format(test, date.strftime('%Y-%m'))),
        _key("participation:{0}:{1}".format(test, date.strftime('%Y-%m-%d'))),
        _key("participation:{0}:{1}:Y"), # with variation name (should settle on variation or alternative)
        _key("participation:{0}:{1}:Y-m"),
        _key("participation:{0}:{1}:Y-m-d"),
    ]
    msetbit(keys=keys,
            args=[_id, 1, _id, 1, _id, 1, _id, 1, _id, 1])


def record_conversion(_id, test, variation, goal, value=None):
    """Record a user's goal conversion with an optional value"""
    pass

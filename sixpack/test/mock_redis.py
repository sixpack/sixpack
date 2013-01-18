import defaultdict


class MockRedis(object):
    """MockRedis class borrowed from
    http://seeknuance.com/2012/02/18/replacing-redis-with-a-python-mock/"""

    # The 'Redis' store
    redis = defaultdict(dict)

    def __init__(self):
        """Initialize the object."""
        pass

    def delete(self, key):  # pylint: disable=R0201
        """Emulate delete."""

        if key in MockRedis.redis:
            del MockRedis.redis[key]

    def exists(self, key):  # pylint: disable=R0201
        """Emulate get."""

        return key in MockRedis.redis

    def get(self, key):  # pylint: disable=R0201
        """Emulate get."""

        # Override the default dict
        result = '' if key not in MockRedis.redis else MockRedis.redis[key]
        return result

    def hget(self, hashkey, attribute):  # pylint: disable=R0201
        """Emulate hget."""

        # Return '' if the attribute does not exist
        result = MockRedis.redis[hashkey][attribute] if attribute in MockRedis.redis[hashkey] \
                 else ''
        return result

    def hgetall(self, hashkey):  # pylint: disable=R0201
        """Emulate hgetall."""

        return MockRedis.redis[hashkey]

    def hlen(self, hashkey):  # pylint: disable=R0201
        """Emulate hlen."""

        return len(MockRedis.redis[hashkey])

    def hmset(self, hashkey, value):  # pylint: disable=R0201
        """Emulate hmset."""

        # Iterate over every key:value in the value argument.
        for attributekey, attributevalue in value.items():
            MockRedis.redis[hashkey][attributekey] = attributevalue

    def hset(self, hashkey, attribute, value):  # pylint: disable=R0201
        """Emulate hset."""

        MockRedis.redis[hashkey][attribute] = value

    def keys(self, pattern):  # pylint: disable=R0201
        """Emulate keys."""
        import re

        # Make a regex out of pattern.
        # The only special matching character we look for is '*'
        regex = '^' + pattern.replace('*', '.*') + '$'

        # Find every key that matches the pattern
        result = [k for k in MockRedis.redis.keys() if re.match(regex, k)]

        return result

    def sadd(self, key, value):  # pylint: disable=R0201
        """Emulate sadd."""

        # Does the set at this key already exist?
        if key in MockRedis.redis:
            # Yes, add this to the set
            MockRedis.redis[key].add(value)
        else:
            # No, override the defaultdict's default and create the set
            MockRedis.redis[key] = set([value])

    def smembers(self, key):  # pylint: disable=R0201
        """Emulate smembers."""

        return MockRedis.redis[key]


def mock_redis_client():
    """Mock common.util.redis_client so we can
    return a MockRedis object instead of a Redis
    object."""
    return MockRedis()

import redis

REDIS = redis.StrictRedis(host='localhost', port=6379, db=0)

from sixpack import db

for key in db.REDIS.keys("sxp:*"):
    db.REDIS.delete(key)

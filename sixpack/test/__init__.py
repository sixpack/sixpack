import os

# HACK: Tests will not run if the SIXPACK_CONFIG is not specified
config_path = os.environ.get('SIXPACK_CONFIG', None)
if config_path is None:
    os.environ['SIXPACK_CONFIG'] = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', '..', '..', 'config.yml'))


from sixpack import db

for key in db.REDIS.keys("sxp:*"):
    db.REDIS.delete(key)

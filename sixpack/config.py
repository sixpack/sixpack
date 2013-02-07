import yaml
import os

config_path = os.environ.get('SIXPACK_CONFIG', None)
if config_path is None:
    raise RuntimeError('SIXPACK_CONFIG environment variable required')

try:
    CONFIG = yaml.safe_load(open(config_path, 'r'))
except IOError:
    raise RuntimeError('SIXPACK_CONFIG - {0} - is an invalid path'.format(config_path))
except yaml.YAMLError, exc:
    raise RuntimeError('Error in configuration file: {0}'.format(str(exc)))

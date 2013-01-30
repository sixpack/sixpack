import random
from datetime import datetime
import re

from db import _key, msetbit, sequential_id

# This is pretty restrictive, but we can always relax it later.
VALID_EXPERIMENT_ALTERNATIVE_RE = re.compile(r"^[a-z0-9][a-z0-9\-_ ]*$", re.I)

class Client(object):

    def __init__(self, client_id, redis_conn):
        self.redis = redis_conn
        self.client_id = client_id
        self._sequential_id = None

    @property
    def sequential_id(self):
        if self._sequential_id is None:
            self._sequential_id = sequential_id('internal_user_ids', self.client_id)
        return self._sequential_id


class ExperimentCollection(object):

    def __init__(self, redis_conn):
        self.redis = redis_conn
        self.experiments = []

    def __iter__(self):
        self.experiments = []
        for exp_key in self.redis.smembers(_key('experiments')):
            self.experiments.append(exp_key)

        return self

    def __next__(self):
        for i in self.experiments:
            yield Experiment.find(i, self.redis)


class Experiment(object):

    def __init__(self, name, alternatives, redis_conn):
        self.name = name
        self.alternatives = Experiment.initialize_alternatives(alternatives, name, redis_conn)
        self.redis = redis_conn

    def save(self):
        if self.is_new_record():
            self.redis.sadd(_key('experiments'), self.name)
            self.redis.set(_key("experiments:{0}".format(self.name)), 0)

        self.redis.hset(self.key(), 'created_at', datetime.now())
        for alternative in reversed(self.alternatives):
            self.redis.lpush("{0}:alternatives".format(self.key()), alternative.name)

    @staticmethod
    def all(redis_conn):
        experiments = []
        keys = redis_conn.smembers(_key('experiments'))
        for key in keys:
            experiments.append(Experiment.find(key, redis_conn))
        # get keys,
        # new experiment collection with all the keys
        return experiments

    def control(self):
        return self.alternatives[0]

    def created_at(self):
        return self.redis.hget(self.key(), 'created_at')

    def get_alternative_names(self):
        return [alt.name for alt in self.alternatives]

    def is_new_record(self):
        return not self.redis.exists(self.key())

    def delete(self):
        # kill the alts first
        self.delete_alternatives()
        self.reset_winner()

        self.redis.srem(_key('experiments'), self.name)
        self.redis.delete(self.key())
        self.increment_version()

    def version(self):
        version = self.redis.get(_key("experiments:{0}".format(self.name)))
        return 0 if version is None else int(version)


    def increment_version(self):
        self.redis.incr(_key('experiments:{0}'.format(self.name)))

    def convert(self, client):
        alternative = self.get_alternative_by_client_id(client)

        if not alternative: # TODO or has already converted?
            raise Exception('this client was not participaing')

        alternative.record_conversion(client)

    def set_winner(self, alternative_name):
        key = "{0}:winner".format(self.key())
        self.redis.set(key, alternative_name)

    def has_winner(self):
        key = "{0}:winner".format(self.key())
        return self.redis.exists(key)

    def get_winner(self):
        if self.has_winner():
            key = "{0}:winner".format(self.key())
            return self.redis.get(key)

        return False

    def reset_winner(self):
        key = "{0}:winner".format(self.key())
        self.redis.delete(key)

    def delete_alternatives(self):
        for alternative in self.alternatives:
            alternative.delete()

    def get_alternative(self, client):
        chosen_alternative = self.get_alternative_by_client_id(client.sequential_id)
        if not chosen_alternative:
            chosen_alternative = self.choose_alternative(client=client)
            chosen_alternative.record_participation(client)

        return chosen_alternative

    def get_alternative_by_client_id(self, client):
        # TODO, THIS IS SCRATCH/PROTO
        # MOVE INTO A LUA SCRIPT
        for alternative in self.get_alternative_names():
            key = _key("participations:{0}:{1}:all".format(self.rawkey(), alternative))
            if self.redis.getbit(key, client.sequential_id):
                return Alternative(alternative, self.name, self.redis)

        return None

    def has_converted_by_client_id(self, client_id):
        # TODO, THIS IS SCRATCH/PROTO
        # MOVE INTO A LUA SCRIPT
        for alternative in self.get_alternative_names():
            key = _key("conversions:{0}:{1}:all".format(self.rawkey(), alternative))
            if self.redis.getbit(key, client_id):
                return True

        return False

    def choose_alternative(self, client=None):
        # This will be hooked up with some fun math-guy-steve stuff later
        return random.choice(self.alternatives)

    def rawkey(self):
        return "{0}/{1}".format(self.name, self.version())

    def key(self):
        key = "experiments:{0}".format(self.rawkey())
        return _key(key)

    @classmethod
    def find(cls, experiment_name, redis_conn):
        if redis_conn.sismember(_key("experiments"), experiment_name):
            return cls(experiment_name, Experiment.load_alternatives(experiment_name, redis_conn), redis_conn)
        else:
            raise Exception('Experiment does not exist')

    @classmethod
    def find_or_create(cls, experiment_name, alternatives, redis_conn):
        if len(alternatives) < 2:
            raise Exception('Must provide at least two alternatives')

        # We don't use the class method key here
        if redis_conn.sismember(_key("experiments"), experiment_name):
            # Note during refactor:
            # We're not instanciating a new Experiment, rather than this load_alternatives hackery
            experiment = Experiment.find(experiment_name, redis_conn)

            # get the existing alternatives
            current_alternatives = experiment.get_alternative_names()

            # Make sure the alternative options are correct.
            # If they are not, then we have to make a new version
            # above `experiment` is then returned eventually
            if sorted(current_alternatives) != sorted(alternatives):
                experiment.increment_version()

                # initialize a new one
                experiment = cls(experiment_name, alternatives, redis_conn)
                experiment.save()

        # completely new experiment
        else:
            experiment = cls(experiment_name, alternatives, redis_conn)
            experiment.save()

        return experiment

    @staticmethod
    def load_alternatives(experiment_name, redis_conn):
        # get latest version of experiment
        version = redis_conn.get(_key("experiments:{0}".format(experiment_name)))
        key = _key("experiments:{0}/{1}:alternatives".format(experiment_name, version))
        return redis_conn.lrange(key, 0, -1)

    @staticmethod
    def initialize_alternatives(alternatives, experiment_name, redis_conn):
        for alternative_name in alternatives:
            if not Alternative.is_valid(alternative_name):
                raise Exception('Invalid alternative name')

        return [Alternative(n, experiment_name, redis_conn) for n in alternatives]

    @staticmethod
    def is_valid(experiment_name):
        return (isinstance(experiment_name, basestring) and \
            VALID_EXPERIMENT_ALTERNATIVE_RE.match(experiment_name) is not None)


class AlternativeCollection(object):

    def __init__(self, redis_conn):
        self.redis = redis_conn
        self.alternatives = []

    # def __iter__(self):
    #     self.alternatives = []
    #     for exp_key in self.redis.smembers(_key('experiments')):
    #         self.experiments.append(exp_key)

    #     return self

    # def __next__(self):
    #     for i in self.alternatives:
    #         yield Experiment.find(i)


class Alternative(object):

    def __init__(self, name, experiment_name, redis_conn):
        self.name = name
        self.experiment_name = experiment_name
        self.redis = redis_conn

    # TODO KEYSPACE
    def reset(self):
        self.redis.delete(_key("conversion:{0}:{1}".format(self.experiment_name, self.name)))
        self.redis.delete(_key("participation:{0}:{1}".format(self.experiment_name, self.name)))

        key = "participation:{0}:{1}*".format(self.experiment_name, self.name)
        participation_keys = self.redis.keys(_key(key))
        for p_key in participation_keys:
            self.redis.delete(p_key)

    def delete(self):
        self.redis.delete(self.key())

    def is_control():
        pass

    def experiment(self):
        return Experiment.find(self.experiment_name, self.redis)

    def participant_count(self):
        key = _key("participations:{0}:{1}".format(self.experiment().rawkey(), self.name))
        return self.redis.bitcount(key)

    def completed_count(self):
        key = _key("conversions:{0}:{1}".format(self.experiment().rawkey(), self.name))
        return self.redis.bitcount(key)

    def record_participation(self, client):
        """Record a user's participation in a test along with a given variation"""
        date = datetime.now()
        experiment_key = self.experiment().rawkey()

        keys = [
            _key("participations:{0}:_all:all".format(experiment_key)),
            _key("participations:{0}:_all:{1}".format(experiment_key, date.strftime('%Y'))),
            _key("participations:{0}:_all:{1}".format(experiment_key, date.strftime('%Y-%m'))),
            _key("participations:{0}:_all:{1}".format(experiment_key, date.strftime('%Y-%m-%d'))),
            _key("participations:{0}:{1}:all".format(experiment_key, self.name)),
            _key("participations:{0}:{1}:{2}".format(experiment_key, self.name, date.strftime('%Y'))),
            _key("participations:{0}:{1}:{2}".format(experiment_key, self.name, date.strftime('%Y-%m'))),
            _key("participations:{0}:{1}:{2}".format(experiment_key, self.name, date.strftime('%Y-%m-%d'))),
        ]
        msetbit(keys=keys, args=([client.sequential_id, 1] * len(keys)))

    def record_conversion(self, client):
        """Record a user's conversion in a test along with a given variation"""
        date = datetime.now()
        experiment_key = self.experiment().rawkey()

        keys = [
            _key("conversions:{0}:_all:users:all".format(experiment_key)),
            _key("conversions:{0}:_all:users:{1}".format(experiment_key, date.strftime('%Y'))),
            _key("conversions:{0}:_all:users:{1}".format(experiment_key, date.strftime('%Y-%m'))),
            _key("conversions:{0}:_all:users:{1}".format(experiment_key, date.strftime('%Y-%m-%d'))),
            _key("conversions:{0}:{1}:users:all".format(experiment_key, self.name)),
            _key("conversions:{0}:{1}:users:{2}".format(experiment_key, self.name, date.strftime('%Y'))),
            _key("conversions:{0}:{1}:users:{2}".format(experiment_key, self.name, date.strftime('%Y-%m'))),
            _key("conversions:{0}:{1}:users:{2}".format(experiment_key, self.name, date.strftime('%Y-%m-%d'))),
        ]
        msetbit(keys=keys, args=([client.sequential_id, 1] * len(keys)))

    def conversion_rate():
        pass

    def z_score():
        pass

    def key(self):
        return _key("{0}:{1}".format(self.experiment_name, self.name))

    @staticmethod
    def is_valid(alternative_name):
        return (isinstance(alternative_name, basestring) and \
            VALID_EXPERIMENT_ALTERNATIVE_RE.match(alternative_name) is not None)

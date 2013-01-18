from datetime import datetime

from db import _key, record_participation

import random

class ExperimentCollection(object):

    def __init__(self, redis_conn):
        self.redis = redis_conn
        self.experiments = []

    # TODO: call redis in __next__
    def __iter__(self):
        self.experiments = []
        for exp_key in self.redis.smembers(_key('experiments')):
            self.experiments.append(Experiment.find(exp_key))

        return self

    def __next__(self):
        for i in self.experiments:
            yield i

class Experiment(object):

    def __init__(self, name, alternatives, redis_conn):
        self.name = name
        self.alternatives = Experiment.initialize_alternatives(alternatives, name, redis_conn)
        self.redis = redis_conn

    def save(self):
        if self.is_new_record():
            self.redis.sadd(_key('experiments'), self.name)
            self.redis.hset(_key('experiment_start_times'), self.name, datetime.now())


            for alternative in reversed(self.alternatives):
                self.redis.lpush(self.key(), alternative.name)
        else:
            pass

    def control(self):
        return self.alternatives[0]

    def start_time():
        pass

    def get_alternative_names(self):
        return [alt.name for alt in self.alternatives]

    def is_new_record(self):
        return not self.redis.exists(self.key())

    def next_alternative():
        pass

    def reset(self):
        for alternative in self.alternatives:
            alternative.reset()

        self.reset_winner()
        self.increment_version()

    def delete(self):
        # kill the alts first
        self.delete_alternatives()
        self.reset_winner()

        self.redis.srem(_key('experiments'), self.name)
        self.redis.delete(_key(self.name))
        self.redis.hdel(_key('experiment_start_times'), self.name)
        self.increment_version()

    def version(self):
        ret = self.redis.get(_key("{0}:version".format(self.name)))
        return 0 if not ret else ret

    def convert(self, client_id):
        alternative = self.get_alternative(client_id)

        if not alternative: # TODO or has already converted?
            raise Exception('this client was not participaing')

        # TODO, there needs to be get alternative NAME vs get alternative
        alt = Alternative(alternative, self.name, self.redis)
        alt.increment_completion()

    def increment_version(self):
        self.redis.incr(_key('{0}:version'.format(self.name)))

    def set_winner():
        pass

    def reset_winner(self):
        self.redis.hdel(_key('experiment_winner'), self.name)

    def delete_alternatives(self):
        for alternative in self.alternatives:
            alternative.delete()

    def get_alternative(self, client_id):
        chosen_alternative = self.get_alternative_by_client_id(client_id)
        if not chosen_alternative:
            chosen_alternative = self.choose_alternative(client_id)
            record_participation(client_id, self.name, chosen_alternative)

        return chosen_alternative

    def get_alternative_by_client_id(self, client_id):
        # TODO, THIS IS SCRATCH/PROTO
        # MOVE INTO A LUA SCRIPT
        alternatives = self.redis.lrange(self.key(), 0, -1)
        for alternative in alternatives:
            if self.redis.getbit(_key("participation:{0}:{1}".format(self.name, alternative)), client_id):
                return alternative

        return None

    def choose_alternative(self, client_id=None):
        return random.choice(self.alternatives).name

    # TODO, Support Versioning
    def key(self):
        return _key(self.name)

    @classmethod
    def find(cls, experiment_name, redis_conn):
        if redis_conn.exists(_key(experiment_name)):
            return cls(experiment_name, Experiment.load_alternatives(experiment_name, redis_conn), redis_conn)
        else:
            raise Exception('Experiment does not exist') # TODO, not sure if necessary (fry)

    @classmethod
    def find_or_create(cls, experiment_name, alternatives, redis_conn):
        if len(alternatives) < 2:
            raise Exception('Must provide at least two alternatives') # Custom Exceptions, Maybe? TODO

        # We don't use the class method key here
        if redis_conn.exists(_key(experiment_name)):
            # get the existing alternatives
            current_alternatives = Experiment.load_alternatives(experiment_name, redis_conn)

            # Make sure the alternative options are correct.
            # If they are not, then we have to make a new version
            if sorted(current_alternatives) == sorted(alternatives):
                experiment = cls(experiment_name, alternatives, redis_conn)
            else:
                # clear out the old experiment
                old_exp = cls(experiment_name, current_alternatives, redis_conn)
                old_exp.reset()
                old_exp.delete_alternatives()

                # initialize a new one
                experiment = cls(experiment_name, alternatives, redis_conn)
                experiment.save()
        else:
            experiment = cls(experiment_name, alternatives, redis_conn)
            experiment.save()

        return experiment

    @staticmethod
    def load_alternatives(experiment_name, redis_conn):
        return redis_conn.lrange(_key(experiment_name), 0, -1)

    @staticmethod
    def initialize_alternatives(alternatives, experiment_name, redis_conn):
        for alternative_name in alternatives:
            if not Alternative.is_valid(alternative_name):
                raise Exception

        return [Alternative(n, experiment_name, redis_conn) for n in alternatives]

class Alternative(object):

    def __init__(self, name, experiment_name, redis_conn):
        self.name = name
        self.experiment_name = experiment_name
        self.redis = redis_conn

    def reset(self):
        self.redis.hset(self.key(), 'participant_count', 0)
        self.redis.hset(self.key(), 'completed_count', 0)

    def delete(self):
        self.redis.delete(self.key())

    def is_control():
        pass

    def experiment(self):
        return Experiment.find(self.experiment_name)

    def participant_count(self):
        ret = self.redis.hget(self.key(), 'participant_count')
        return 0 if not ret else ret

    def completed_count(self):
        ret = self.redis.hget(self.key(), 'completed_count')
        return 0 if not ret else ret

    def increment_participation(self):
        self.redis.hincrby(self.key(), 'participant_count', 1)

    def increment_completion(self):
        self.redis.hincrby(self.key(), 'completed_count', 1)

    def conversion_rate():
        pass

    def z_score():
        pass

    def key(self):
        return _key("{0}:{1}".format(self.experiment_name, self.name))

    @staticmethod
    def is_valid(alternative_name):
        return isinstance(alternative_name, basestring)

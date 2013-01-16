from datetime import datetime

from db import REDIS, _key, record_participation
from alternative import Alternative
import random

class Experiment(object):

    def __init__(self, name, alternatives):
        self.name = name
        self.alternatives = Experiment.initialize_alternatives(alternatives, name)

    def save(self):
        if self.is_new_record():
            REDIS.sadd(_key('experiments'), self.name)
            REDIS.hset(_key('experiment_start_times'), self.name, datetime.now())


            for alternative in reversed(self.alternatives):
                REDIS.lpush(self.key(), alternative.name)
        else:
            pass

    def control():
        pass

    def start_time():
        pass

    def get_alternative_names():
        pass

    def is_new_record(self):
        return not REDIS.exists(self.key())

    def next_alternative():
        pass

    def random_alternative():
        pass

    def reset(self):
        for alternative in self.alternatives:
            alternative.reset()
        self.reset_winner()
        self.increment_version()

    def delete():
        pass

    def version():
        pass

    def increment_version(self):
        REDIS.incr(_key('{0}:version'.format(self.name)))

    def set_winner():
        pass

    def reset_winner(self):
        REDIS.hdel(_key('experiment_winner'), self.name)

    def delete_alternatives(self):
        for alternative in self.alternatives:
            alternative.delete()

    def get_alternative(self, client_id):
        # TODO, THIS IS SCRATCH/PROTO
        # MOVE INTO A LUA SCRIPT
        alternatives = REDIS.lrange(self.key(), 0, -1)
        for alternative in alternatives:
            if REDIS.getbit(_key("participation:{0}:{1}".format(self.name, alternative)), client_id):
                return alternative

        chosen_alternative = self.choose_alternative(client_id)
        record_participation(client_id, self.name, chosen_alternative)

        return chosen_alternative

    def choose_alternative(self, client_id):
        return random.choice(self.alternatives).name

# psudo code for is participating
# get key for experiment name
# alts = key lrange 0 -1
# for each alt
#    sismember alt key:participation client_id
#    if true return alt
#
# get random choice (MGS will do something here, most likely)
# record participation(client, test, random variation)

    # TODO, Support Versioning
    def key(self):
        return _key(self.name)

    @classmethod
    def all():
        pass

    @classmethod
    def find(cls, experiment_name):
        if REDIS.exists(_key(experiment_name)):
            return cls(experiment_name, Experiment.load_alternatives(experiment_name))
        else:
            raise Exception('Experiment does not exist') # TODO, not sure if necessary (fry)

    @classmethod
    def find_or_create(cls, experiment_name, alternatives):
        if len(alternatives) < 2:
            raise Exception('Must provide at least two alternatives') # Custom Exceptions, Maybe? TODO

        # We don't use the class method key here
        if REDIS.exists(_key(experiment_name)):
            # get the existing alternatives
            current_alternatives = Experiment.load_alternatives(experiment_name)

            # Make sure the alternative options are correct.
            # If they are not, then we have to make a new version
            if sorted(current_alternatives) == sorted(alternatives):
                experiment = cls(experiment_name, alternatives)
            else:
                # clear out the old experiment
                old_exp = cls(experiment_name, current_alternatives)
                old_exp.reset()
                old_exp.delete_alternatives()

                # initialize a new one
                experiment = cls(experiment_name, alternatives)
                experiment.save()
        else:
            experiment = cls(experiment_name, alternatives)
            experiment.save()

        return experiment

    @staticmethod
    def load_alternatives(experiment_name):
        return REDIS.lrange(_key(experiment_name), 0, -1)

    @staticmethod
    def initialize_alternatives(alternatives, experiment_name):
        for alternative_name in alternatives:
            if not Alternative.is_valid(alternative_name):
                raise Exception

        return [Alternative(n, experiment_name) for n in alternatives]
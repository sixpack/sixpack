from db import REDIS, _key

class Alternative(object):

    def __init__(self, name, experiment_name):
        self.name = name
        self.experiment_name = experiment_name

    def reset(self):
        REDIS.hset(self.key(), 'participant_count', 0)
        REDIS.hset(self.key(), 'completed_count', 0)

    def delete(self):
        REDIS.delete(self.key())

    def is_control():
        pass

    def experiment():
        pass

    def increment_participation():
        pass

    def participant_count():
        pass

    def completed_count():
        pass

    def increment_completion():
        pass

    def conversion_rate():
        pass

    def z_score():
        pass

    @staticmethod
    def is_valid(alternative_name):
        return isinstance(alternative_name, basestring)

    def key(self):
        _key("{0}:{1}".format(self.experiment_name, self.name))

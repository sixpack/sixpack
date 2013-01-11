class Alternative(object):

    def __init__(self, name, experiment_name):
        self.name = name
        self.experiment_name = experiment_name

    def get_name():
        pass

    def experiment_name():
        pass

    def reset():
        pass

    def delete():
        pass

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

    @staticmethod
    def key():
        pass

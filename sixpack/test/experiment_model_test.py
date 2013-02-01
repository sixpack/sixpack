import unittest
from numbers import Number
from mock import MagicMock
from sixpack.db import REDIS, _key

from sixpack.models import Experiment

class TestExperimentModel(unittest.TestCase):

    unit = True

    def setUp(self):
        self.redis = MagicMock(REDIS)
        self.alternatives = ['yes', 'no']

    # def test_key(self):
    #     exp = Experiment('show-something', self.alternatives, self.redis)
    #     key = exp.key()
    #     self.redis.reset_mock()
    #     self.redis.get.return_value = 0
    #     self.assertEqual(key, 'sixpack:experiments:show-something/0')
    #     self.redis.reset_mock()

    def test_is_not_valid(self):
        not_valid = Experiment.is_valid(1)
        self.assertFalse(not_valid)

        not_valid = Experiment.is_valid(':123:name')
        self.assertFalse(not_valid)

        not_valid = Experiment.is_valid('_123name')
        self.assertFalse(not_valid)

        not_valid = Experiment.is_valid('&123name')
        self.assertFalse(not_valid)

    def test_save(self):
        pass

    def test_control(self):
        pass

    def test_start_time(self):
        pass

    def test_get_alternative_names(self):
        exp = Experiment('show-something', self.alternatives, self.redis)
        names = exp.get_alternative_names()
        self.assertEqual(sorted(self.alternatives), sorted(names))

    def test_is_new_record(self):
        exp = Experiment('show-something', self.alternatives, self.redis)
        exp.is_new_record()
        self.redis.sismember.assert_called_once_with(_key('experiments'), exp.name)

    def test_next_alternative(self):
        pass

    def test_reset(self):
        alt_count = len(self.alternatives)
        print alt_count
        pass


    def test_delete(self):
        pass

    def test_version(self):
        self.redis.get.return_value = 0

        exp = Experiment('show-something', self.alternatives, self.redis)
        version = exp.version()

        self.redis.get.assert_called_once_with(_key("experiments:{0}".format(exp.name)))
        self.assertTrue(isinstance(version, Number))

        self.redis.reset_mock()

    def test_convert(self):
        pass

    def test_increment_version(self):
        exp = Experiment('show-something', self.alternatives, self.redis)
        exp.increment_version()
        self.redis.incr.assert_called_once_with(_key("experiments:{0}".format(exp.name)))

    def test_set_winner(self):
        pass

    def test_reset_winner(self):
        exp = Experiment('show-something', self.alternatives, self.redis)
        exp.reset_winner()
        key = "{0}:winner".format(exp.key())
        self.redis.delete.assert_called_once_with(key)

    def test_delete_alternatives(self):
        pass

    def test_get_alternative(self):
        pass

    def test_choose_alternative(self):
        exp = Experiment('show-something', self.alternatives, self.redis)
        alt = exp.choose_alternative()

        self.assertIn(alt.name, self.alternatives)
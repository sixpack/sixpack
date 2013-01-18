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

    def test_key(self):
        exp = Experiment('show-something', self.alternatives, self.redis)
        key = exp.key()
        self.assertEqual(key, 'sixpack:show-something')

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
        self.redis.exists.assert_called_once_with(exp.key())

    def test_next_alternative(self):
        pass

    def test_reset(self):
        alt_count = len(self.alternatives)
        print alt_count
        pass


    def test_delete(self):
        pass

    def test_version(self):
        self.redis.get.return_value = 1

        exp = Experiment('show-something', self.alternatives, self.redis)
        version = exp.version()

        self.redis.get.assert_called_once_with(_key("{0}:version".format(exp.name)))
        self.assertTrue(isinstance(version, Number))

        self.redis.reset_mock()

    def test_convert(self):
        pass

    def test_increment_version(self):
        exp = Experiment('show-something', self.alternatives, self.redis)
        exp.increment_version()
        self.redis.incr.assert_called_once_with(_key("{0}:version".format(exp.name)))

    def test_set_winner(self):
        pass

    def test_reset_winner(self):
        exp = Experiment('show-something', self.alternatives, self.redis)
        exp.reset_winner()
        self.redis.hdel.assert_called_once_with(_key('experiment_winner'), exp.name)

    def test_delete_alternatives(self):
        pass

    def test_get_alternative(self):
        pass

    def test_choose_alternative(self):
        exp = Experiment('show-something', self.alternatives, self.redis)
        alt = exp.choose_alternative()

        self.assertIn(alt, self.alternatives)
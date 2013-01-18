import unittest
from numbers import Number
from mock import MagicMock
from sixpack.db import REDIS

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

import unittest

import sixpack
from sixpack.models import Experiment


class TestWeights(unittest.TestCase):

    def test_uniform(self):
        exp = Experiment("test", ["no", "yes"])
        self.assertFalse(exp.is_weighted())
        for alternative in exp.alternatives:
            self.assertIsNone(alternative.weight)

    def test_weighted(self):
        exp = Experiment("test", ["no:70", "yes:30"])
        self.assertTrue(exp.is_weighted())
        for alternative in exp.alternatives:
            self.assertIsNotNone(alternative.weight)
            self.assertIsInstance(alternative.weight, int)
            
    def test_weighted_multi(self):
        exp = Experiment("test", ["no:50", "yes:25", "maybe:25"])
        self.assertTrue(exp.is_weighted())
        for alternative in exp.alternatives:
            self.assertIsNotNone(alternative.weight)
            self.assertIsInstance(alternative.weight, int)

    def test_wrong_weights(self):
        exp = Experiment("test", ["no:70", "yes:20"])
        self.assertFalse(exp.is_weighted())
        exp = Experiment("test", ["no:70", "yes:40"])
        self.assertFalse(exp.is_weighted())

    def test_choices(self):
        exp = Experiment("test", ["no:70", "yes:30"], traffic_fraction=1)
        stats = {}
        N = 100000
        for i in range(N):
            a,_ = exp.choose_alternative("abc")
            stats[a.name] = stats.get(a.name,0) + 1
            
        self.assertGreater(stats['no'], stats['yes'])
        self.assertAlmostEqual(stats['no']/float(N), 0.7, places=1)
        self.assertAlmostEqual(stats['yes']/float(N), 0.3, places=1)
        
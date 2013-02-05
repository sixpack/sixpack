import unittest
from numbers import Number
import fakeredis
from sixpack.db import _key

from sixpack.models import Experiment


class TestExperimentModel(unittest.TestCase):

    unit = True

    def setUp(self):
        self.redis = fakeredis.FakeStrictRedis()
        self.alternatives = ['yes', 'no']

        self.exp_1 = Experiment('show-something-awesome', self.alternatives, self.redis)
        self.exp_2 = Experiment('dales-lagunitas', ['dales', 'lagunitas'], self.redis)
        self.exp_3 = Experiment('mgd-budheavy', ['mgd', 'bud-heavy'], self.redis)
        self.exp_1.save()
        self.exp_2.save()
        self.exp_3.save()

    def test_key(self):
        key = self.exp_1.key()
        self.assertEqual(key, 'sixpack:experiments:show-something-awesome/0')

        key_2 = self.exp_2.key()
        self.assertEqual(key_2, 'sixpack:experiments:dales-lagunitas/0')

        exp = Experiment('brews', ['mgd', 'bud-heavy'], self.redis)
        exp.increment_version()
        key_3 = exp.key()
        self.assertEqual(key_3, 'sixpack:experiments:brews/1')

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
        control = self.exp_1.control()
        self.assertEqual(control.name, 'yes')

    def test_start_time(self):
        pass

    def test_get_alternative_names(self):
        exp = Experiment('show-something', self.alternatives, self.redis)
        names = exp.get_alternative_names()
        self.assertEqual(sorted(self.alternatives), sorted(names))

    def test_is_new_record(self):
        exp = Experiment('show-something-is-new-record', self.alternatives, self.redis)
        self.assertTrue(exp.is_new_record())
        exp.save()
        self.assertFalse(exp.is_new_record())

    def test_reset(self):
        alt_count = len(self.alternatives)
        print alt_count
        pass

    def test_delete(self):
        exp = Experiment('delete-me', self.alternatives, self.redis)
        exp.save()

        exp.delete()
        with self.assertRaises(Exception):
            Experiment.find('delete-me', self.alternatives, self.redis)

    def test_archive(self):
        self.assertFalse(self.exp_1.is_archived())
        self.exp_1.archive()
        self.assertTrue(self.exp_1.is_archived())
        self.exp_1.unarchive()
        self.assertFalse(self.exp_1.is_archived())

    def test_version(self):
        pass

    def test_convert(self):
        pass

    def test_increment_version(self):
        original_version = self.exp_3.version()
        self.exp_3.increment_version()
        new_version = self.exp_3.version()
        difference = new_version - original_version
        self.assertEqual(difference, 1)

    def test_set_winner(self):
        exp = Experiment('test-winner', ['1', '2'], self.redis)
        exp.set_winner('1')
        self.assertTrue(exp.has_winner())

        exp.set_winner('1')
        winner = exp.get_winner()
        self.assertEqual(winner, '1')

    def test_has_winner(self):
        exp = Experiment('test-winner', ['1', '2'], self.redis)
        self.assertFalse(exp.has_winner())

    def test_reset_winner(self):
        exp = Experiment('show-something-reset-winner', self.alternatives, self.redis)
        exp.save()
        exp.set_winner('yes')
        self.assertTrue(exp.has_winner())
        self.assertEqual(exp.get_winner(), 'yes')

        exp.reset_winner()
        self.assertFalse(exp.has_winner())

    def test_delete_alternatives(self):
        pass

    def test_get_alternative(self):
        pass

    # disabled test, fakeredis doesn't support bitcount
    def _test_choose_alternative(self):
        exp = Experiment('show-something', self.alternatives, self.redis)
        exp.save()
        alt = exp.choose_alternative()

        self.assertIn(alt.name, self.alternatives)

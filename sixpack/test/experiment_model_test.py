import unittest
# from numbers import Number
# from sixpack.db import _key
from datetime import datetime

import fakeredis

from sixpack.models import Experiment, Alternative, Client


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

    def test_constructor(self):
        with self.assertRaises(ValueError):
            Experiment('not-enough-args', ['1'], self.redis)

    def test_save(self):
        pass

    def test_control(self):
        control = self.exp_1.control()
        self.assertEqual(control.name, 'yes')

    def test_created_at(self):
        exp = Experiment('bench-press', ['joe', 'think'], self.redis)
        date = exp.created_at()
        self.assertIsNone(date)
        exp.save()
        date = exp.created_at()
        self.assertTrue(isinstance(date, datetime))

    def test_get_alternative_names(self):
        exp = Experiment('show-something', self.alternatives, self.redis)
        names = exp.get_alternative_names()
        self.assertEqual(sorted(self.alternatives), sorted(names))

    def test_is_new_record(self):
        exp = Experiment('show-something-is-new-record', self.alternatives, self.redis)
        self.assertTrue(exp.is_new_record())
        exp.save()
        self.assertFalse(exp.is_new_record())

    # fakeredis does not currently support bitcount
    # todo, fix fakeredis and
    def _test_total_participants(self):
        pass

    def _test_total_conversions(self):
        pass

    def test_description(self):
        exp = Experiment.find_or_create('never-gonna', ['give', 'you', 'up'], self.redis)
        self.assertEqual(exp.get_description(), '')

        exp.update_description('hallo')
        self.assertEqual(exp.get_description(), 'hallo')

    def test_reset(self):
        exp = Experiment.find_or_create('never-gonna-x', ['let', 'you', 'down'], self.redis)
        exp.reset()

        self.assertEqual(exp.version(), 1)

    def test_delete(self):
        exp = Experiment('delete-me', self.alternatives, self.redis)
        exp.save()

        exp.delete()
        with self.assertRaises(ValueError):
            Experiment.find('delete-me', self.redis)

    def test_archive(self):
        self.assertFalse(self.exp_1.is_archived())
        self.exp_1.archive()
        self.assertTrue(self.exp_1.is_archived())
        self.exp_1.unarchive()
        self.assertFalse(self.exp_1.is_archived())

    def test_unarchive(self):
        self.exp_1.archive()
        self.assertTrue(self.exp_1.is_archived())
        self.exp_1.unarchive()
        self.assertFalse(self.exp_1.is_archived())

    def test_version(self):
        pass

    def test_increment_version(self):
        original_version = self.exp_3.version()
        self.exp_3.increment_version()
        new_version = self.exp_3.version()
        difference = new_version - original_version
        self.assertEqual(difference, 1)

    def test_convert(self):
        pass

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

    def test_get_winner(self):
        exp = Experiment.find_or_create('test-get-winner', ['1', '2'], self.redis)
        self.assertIsNone(exp.get_winner())

        exp.set_winner('1')
        self.assertEqual(exp.get_winner(), '1')

    def test_reset_winner(self):
        exp = Experiment('show-something-reset-winner', self.alternatives, self.redis)
        exp.save()
        exp.set_winner('yes')
        self.assertTrue(exp.has_winner())
        self.assertEqual(exp.get_winner(), 'yes')

        exp.reset_winner()
        self.assertFalse(exp.has_winner())

    def test_winner_key(self):
        exp = Experiment.find_or_create('winner-key', ['win', 'lose'], self.redis)
        self.assertEqual(exp._winner_key, "{0}:winner".format(exp.key()))

    def test_get_alternative(self):
        client = Client(10, self.redis)
        client._sequential_id = 100

        exp = Experiment.find_or_create('archived-control', ['w', 'l'], self.redis)
        exp.archive()

        # should return control on archived test with no winner
        alt = exp.get_alternative(client)
        self.assertEqual(alt.name, 'w')

        # should return current participation
        exp.unarchive()
        ### HACK TO SKIP WHIPLASH TESTS
        exp.random_sample = 1
        ### HACK TO SKIP WHIPLASH TESTS

        selected_for_client = exp.get_alternative(client)
        self.assertIn(selected_for_client.name, ['w', 'l'])

        # should check to see if client is participating and only return the same alt
        # unsure how to currently test since fakeredis obviously doesn't parse lua
        # most likely integration tests

    # See above note for the next 5 tests
    def _test_get_alternative_by_client_id(self):
        pass

    def _test_has_converted_by_client(self):
        pass

    def _test_choose_alternative(self):
        pass

    def _test_random_choice(self):
        pass

    def _test_whiplash(self):
        pass

    def test_raw_key(self):
        exp = Experiment.find_or_create('monkey', ['patch', 'banana'], self.redis)
        self.assertEqual(exp.rawkey(), 'monkey/0')

    def test_key(self):
        key = self.exp_1.key()
        self.assertEqual(key, 'sixpack:experiments:show-something-awesome/0')

        key_2 = self.exp_2.key()
        self.assertEqual(key_2, 'sixpack:experiments:dales-lagunitas/0')

        exp = Experiment('brews', ['mgd', 'bud-heavy'], self.redis)
        exp.increment_version()
        key_3 = exp.key()
        self.assertEqual(key_3, 'sixpack:experiments:brews/1')

    def test_find(self):
        exp = Experiment('crunches-situps', ['crunches', 'situps'], self.redis)
        exp.save()

        self.assertEqual(exp.version(), 0)

        with self.assertRaises(ValueError):
            Experiment.find('this-does-not-exist', self.redis)

        try:
            Experiment.find('crunches-situps', self.redis)
        except:
            self.fail('known exp not found')

    def test_find_or_create(self):
        # should throw a ValueError if alters are invalid
        with self.assertRaises(ValueError):
            Experiment.find_or_create('party-time', ['1'], self.redis)

        with self.assertRaises(ValueError):
            Experiment.find_or_create('party-time', ['1', '*****'], self.redis)

        # should create a -NEW- experiment if experiment has never been used
        with self.assertRaises(ValueError):
            Experiment.find('dance-dance', self.redis)

        exp_1 = Experiment.find_or_create('dance-dance', ['1', '2'], self.redis)
        self.assertEqual(exp_1.version(), 0)

        # should return an -existing- experiment if found correctly
        try:
            exp_2 = Experiment.find('dance-dance', self.redis)
            self.assertEqual(exp_2.version(), 0)
        except:
            self.fail('known exp not found')

        # should increment version if the experiment exists but alts changed
        exp_3 = Experiment.find_or_create('dance-dance', ['2', '3'], self.redis)
        self.assertEqual(exp_3.version(), 1)

    def test_all(self):
        # there are three created in setUp()
        all_of_them = Experiment.all(self.redis)
        self.assertEqual(len(all_of_them), 3)

        exp_1 = Experiment('archive-this', ['archived', 'unarchive'], self.redis)
        exp_1.save()

        all_again = Experiment.all(self.redis)
        self.assertEqual(len(all_again), 4)

        exp_1.archive()
        all_archived = Experiment.all(self.redis)
        self.assertEqual(len(all_archived), 3)

        all_with_archived = Experiment.all(self.redis, False)
        self.assertEqual(len(all_with_archived), 4)

    def test_load_alternatives(self):
        exp = Experiment.find_or_create('load-alts-test', ['yes', 'no', 'call-me-maybe'], self.redis)
        alts = Experiment.load_alternatives(exp.name, self.redis)
        self.assertEqual(sorted(alts), sorted(['yes', 'no', 'call-me-maybe']))

        exp = Experiment.find_or_create('load-alts-test', ['yes', 'no'], self.redis)
        alts = Experiment.load_alternatives(exp.name, self.redis)
        self.assertEqual(sorted(alts), sorted(['yes', 'no']))

    def _test_initialize_alternatives(self):
        # Should throw ValueError
        with self.assertRaises(ValueError):
            Experiment.initialize_alternatives('n', ['*'], self.redis)

        # each item in list should be Alternative Instance
        alt_objs = Experiment.initialize_alternatives('n', ['1', '2', '3'])
        for alt in alt_objs:
            self.assertTrue(isinstance(alt, Alternative))
            self.assertTrue(alt.name in ['1', '2', '3'])

    def test_is_not_valid(self):
        not_valid = Experiment.is_valid(1)
        self.assertFalse(not_valid)

        not_valid = Experiment.is_valid(':123:name')
        self.assertFalse(not_valid)

        not_valid = Experiment.is_valid('_123name')
        self.assertFalse(not_valid)

        not_valid = Experiment.is_valid('&123name')
        self.assertFalse(not_valid)

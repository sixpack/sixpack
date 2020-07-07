import unittest
# from numbers import Number
# from sixpack.db import _key
from datetime import datetime

import fakeredis
import redis

from sixpack.models import Experiment, Alternative, Client
from sixpack.db import _key

class FakePipelineRaisesWatchError(fakeredis.FakePipeline):

    def execute(self):
        raise redis.WatchError


class TestExperimentModel(unittest.TestCase):

    unit = True

    def setUp(self):
        self.redis = fakeredis.FakeStrictRedis()
        self.alternatives = ['yes', 'no']

        self.exp_1 = Experiment('show-something-awesome', self.alternatives, redis=self.redis)
        self.exp_2 = Experiment('dales-lagunitas', ['dales', 'lagunitas'], redis=self.redis)
        self.exp_3 = Experiment('mgd-budheavy', ['mgd', 'bud-heavy'], redis=self.redis)
        self.exp_1.save()
        self.exp_2.save()
        self.exp_3.save()

    def tearDown(self):
        pipe = self.redis.pipeline()
        pipe.flushdb()
        pipe.execute()

    def test_constructor(self):
        with self.assertRaises(ValueError):
            Experiment('not-enough-args', ['1'], redis=self.redis)

    def test_save(self):
        pass

    def test_control(self):
        control = self.exp_1.control
        self.assertEqual(control.name, 'yes')

    def test_created_at(self):
        exp = Experiment('bench-press', ['joe', 'think'], redis=self.redis)
        date = exp.created_at
        self.assertIsNone(date)
        exp.save()
        date = exp.created_at
        self.assertTrue(isinstance(date, str))

    def test_get_alternative_names(self):
        exp = Experiment('show-something', self.alternatives, redis=self.redis)
        names = exp.get_alternative_names()
        self.assertEqual(sorted(self.alternatives), sorted(names))

    def test_is_new_record(self):
        exp = Experiment('show-something-is-new-record', self.alternatives, redis=self.redis)
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
        exp = Experiment.find_or_create('never-gonna', ['give', 'you', 'up'], redis=self.redis)
        self.assertEqual(exp.description, None)

        exp.update_description('hallo')
        self.assertEqual(exp.description, 'hallo')

    def test_change_alternatives(self):
        exp = Experiment.find_or_create('never-gonna-x', ['let', 'you', 'down'], redis=self.redis)

        with self.assertRaises(ValueError):
            Experiment.find_or_create('never-gonna-x', ['let', 'you', 'down', 'give', 'you', 'up'], redis=self.redis)

        exp.delete()

        Experiment.find_or_create('never-gonna-x', ['let', 'you', 'down', 'give', 'you', 'up'], redis=self.redis)

    def test_delete(self):
        exp = Experiment('delete-me', self.alternatives, redis=self.redis)
        exp.save()

        exp.delete()
        with self.assertRaises(ValueError):
            Experiment.find('delete-me', redis=self.redis)

    def test_leaky_delete(self):
        exp = Experiment('delete-me-1', self.alternatives, redis=self.redis)
        exp.save()

        exp2 = Experiment('delete', self.alternatives, redis=self.redis)
        exp2.save()

        exp2.delete()
        exp3 = Experiment.find('delete-me-1', redis=self.redis)
        self.assertEqual(exp3.get_alternative_names(), self.alternatives)

    def test_archive(self):
        self.assertFalse(self.exp_1.is_archived())
        self.exp_1.archive()
        self.assertTrue(self.exp_1.is_archived())


    def test_pause(self):
        self.assertFalse(self.exp_1.is_paused())
        self.exp_1.pause()
        self.assertTrue(self.exp_1.is_paused())
        self.exp_1.resume()
        self.assertFalse(self.exp_1.is_paused())

    def test_resume(self):
        self.exp_1.pause()
        self.assertTrue(self.exp_1.is_paused())
        self.exp_1.resume()
        self.assertFalse(self.exp_1.is_paused())

    def test_set_winner(self):
        exp = Experiment('test-winner', ['1', '2'], redis=self.redis)
        exp.set_winner('1')
        self.assertTrue(exp.winner is not None)

        exp.set_winner('1')
        self.assertEqual(exp.winner.name, '1')

    def test_winner(self):
        exp = Experiment.find_or_create('test-get-winner', ['1', '2'], redis=self.redis)
        self.assertIsNone(exp.winner)

        exp.set_winner('1')
        self.assertEqual(exp.winner.name, '1')

    def test_reset_winner(self):
        exp = Experiment('show-something-reset-winner', self.alternatives, redis=self.redis)
        exp.save()
        exp.set_winner('yes')
        self.assertTrue(exp.winner is not None)
        self.assertEqual(exp.winner.name, 'yes')

        exp.reset_winner()
        self.assertIsNone(exp.winner)

    def test_winner_key(self):
        exp = Experiment.find_or_create('winner-key', ['win', 'lose'], redis=self.redis)
        self.assertEqual(exp._winner_key, "{0}:winner".format(exp.key()))

    def test_get_alternative(self):
        client = Client(10, redis=self.redis)

        exp = Experiment.find_or_create('pause-control', ['w', 'l'], redis=self.redis)
        exp.pause()

        # should return control on paused test with no winner
        alt = exp.get_alternative(client)
        self.assertEqual(alt.name, 'w')

        # should return current participation
        exp.resume()

        # should be one or the other.
        # @todo, this test is not really testing anything.
        selected_for_client = exp.get_alternative(client)
        self.assertIn(selected_for_client.name, ['w', 'l'])

        # should check to see if client is participating and only return the same alt
        # unsure how to currently test since fakeredis obviously doesn't parse lua
        # most likely integration tests
        exp.archive()

        # test if the redis key is no longer present
        self.redis.get(_key('e:{0}:users'.format(exp.name)))

        # should return control on archived test
        alt = exp.get_alternative(client)
        self.assertEqual(alt.name, 'w')

    def test_reset_experiment(self):
        client = Client(10, redis=self.redis)
        exp = Experiment.find_or_create('reset-test', ['w', 'l'], redis=self.redis)
        exp.get_alternative(client)

        # archive and afterwards reset to see if we 
        # actually reset the data.
        exp.archive()
        self.assertEqual(exp.is_archived(), True)
        exp.reset()
        self.assertEqual(exp.is_archived(), False)

    # See above note for the next 5 tests
    def _test_existing_alternative(self):
        pass

    def _test_has_converted_by_client(self):
        pass

    def _test_choose_alternative(self):
        pass

    def _test_random_choice(self):
        pass

    def test_find(self):
        exp = Experiment('crunches-situps', ['crunches', 'situps'], redis=self.redis)
        exp.save()

        with self.assertRaises(ValueError):
            Experiment.find('this-does-not-exist', redis=self.redis)

        try:
            Experiment.find('crunches-situps', redis=self.redis)
        except:
            self.fail('known exp not found')

    def test_find_or_create(self):
        # should throw a ValueError if alters are invalid
        with self.assertRaises(ValueError):
            Experiment.find_or_create('party-time', ['1'], redis=self.redis)

        with self.assertRaises(ValueError):
            Experiment.find_or_create('party-time', ['1', '*****'], redis=self.redis)

        # should create a -NEW- experiment if experiment has never been used
        with self.assertRaises(ValueError):
            Experiment.find('dance-dance', redis=self.redis)

    def test_all(self):
        # there are three created in setUp()
        all_of_them = Experiment.all(redis=self.redis)
        self.assertEqual(len(all_of_them), 3)

        exp_1 = Experiment('archive-this', ['archived', 'archived2'], redis=self.redis)
        exp_1.save()

        # Check if we have 4 active experiments in total
        all_again = Experiment.all(redis=self.redis)
        self.assertEqual(len(all_again), 4)

        # Pause one experiment.
        exp_1.pause()
        # We should have 1 paused experiment in total
        all_paused = Experiment.paused(redis=self.redis)
        self.assertEqual(len(all_paused), 1)

        # We should have 3 active experiments.
        all_active_experiments = Experiment.all(redis=self.redis)
        self.assertEqual(len(all_active_experiments), 3)

        # Total, with paused and excluding archived should be 4.
        all_with_paused = Experiment.all(exclude_paused=False, redis=self.redis)
        self.assertEqual(len(all_with_paused), 4)

        # Resume the experiment
        exp_1.resume()
        # We should have 4 active experiments
        all_active_experiments = Experiment.all(redis=self.redis)
        self.assertEqual(len(all_active_experiments), 4)        

        # Archive the experiment
        exp_1.archive()
        all_active_experiments = Experiment.all(redis=self.redis)
        self.assertEqual(len(all_active_experiments), 3)

        # We should have 1 archived experiment
        all_archived = Experiment.archived(redis=self.redis)
        self.assertEqual(len(all_archived), 1)

        # Total, with archived, excluding paused should be 4
        all_with_archived = Experiment.all(exclude_archived=False, redis=self.redis)
        self.assertEqual(len(all_with_archived), 4)

    def test_load_alternatives(self):
        exp = Experiment.find_or_create('load-alts-test', ['yes', 'no', 'call-me-maybe'], redis=self.redis)
        alts = Experiment.load_alternatives(exp.name, redis=self.redis)
        self.assertEqual(sorted(alts), sorted(['yes', 'no', 'call-me-maybe']))

    def test_differing_alternatives_fails(self):
        exp = Experiment.find_or_create('load-differing-alts', ['yes', 'zack', 'PBR'], redis=self.redis)
        alts = Experiment.load_alternatives(exp.name, redis=self.redis)
        self.assertEqual(sorted(alts), sorted(['PBR', 'yes', 'zack']))

        with self.assertRaises(ValueError):
            exp = Experiment.find_or_create('load-differing-alts', ['kyle', 'zack', 'PBR'], redis=self.redis)

    def _test_initialize_alternatives(self):
        # Should throw ValueError
        with self.assertRaises(ValueError):
            Experiment.initialize_alternatives('n', ['*'], redis=self.redis)

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

    def test_valid_options(self):
        Experiment.find_or_create('red-white', ['red', 'white'], traffic_fraction=1, redis=self.redis)
        Experiment.find_or_create('red-white-2', ['red', 'white'], traffic_fraction=0.4, redis=self.redis)

    def test_invalid_traffic_fraction(self):
        with self.assertRaises(ValueError):
            Experiment.find_or_create('dist-2', ['dist', '2'], traffic_fraction=2, redis=self.redis)

        with self.assertRaises(ValueError):
            Experiment.find_or_create('dist-100', ['dist', '100'], traffic_fraction=101, redis=self.redis)

        with self.assertRaises(ValueError):
            Experiment.find_or_create('dist-100', ['dist', '100'], traffic_fraction="x", redis=self.redis)

    def test_dont_fail_when_participating_in_nondefault_traffic_experiment_without_traffic_param(self):
        Experiment.find_or_create('red-white', ['red', 'white'], traffic_fraction=0.5, redis=self.redis)
        Experiment.find_or_create('red-white', ['red', 'white'], redis=self.redis)

    def test_changing_traffic_fraction_succeeds(self):
        exp = Experiment.find_or_create('red-white', ['red', 'white'], traffic_fraction=1, redis=self.redis)
        self.assertEqual(exp._traffic_fraction, 1)
        exp = Experiment.find_or_create('red-white', ['red', 'white'], traffic_fraction=0.4, redis=self.redis)
        self.assertEqual(exp._traffic_fraction, 0.4)

    def test_save_with_conflict_persists_traffic_fraction(self):
        def fake_pipeline(transaction=True):
            return FakePipelineRaisesWatchError(self.redis, transaction)

        real_pipeline = self.redis.pipeline
        self.redis.pipeline = fake_pipeline

        # this experiment encounters a WatchError upon saving and only
        # persists its traffic_fraction...
        exp = Experiment('experiment', self.alternatives, redis=self.redis)
        exp.set_traffic_fraction(0.5)
        exp.save()

        self.redis.pipeline = real_pipeline

        # ...and a later instance can recover that traffic fraction
        same_exp = Experiment('experiment', self.alternatives, redis=self.redis)
        self.assertEqual(same_exp.traffic_fraction, 0.5)

    def test_valid_traffic_fractions_save(self):
        # test the hidden prop gets set
        exp = Experiment.find_or_create('dist-02', ['dist', '100'], traffic_fraction=0.02, redis=self.redis)
        self.assertEqual(exp._traffic_fraction, 0.02)

        exp = Experiment.find_or_create('dist-100', ['dist', '100'], traffic_fraction=0.4, redis=self.redis)
        self.assertEqual(exp._traffic_fraction, 0.40)

    # test is set in redis
    def test_traffic_fraction(self):
        exp = Experiment.find_or_create('d-test-10', ['d', 'c'], traffic_fraction=0.1, redis=self.redis)
        exp.save()
        self.assertEqual(exp.traffic_fraction, 0.1)

    def test_valid_kpi(self):
        ret = Experiment.validate_kpi('hello-jose')
        self.assertTrue(ret)
        ret = Experiment.validate_kpi('123')
        self.assertTrue(ret)
        ret = Experiment.validate_kpi('foreigner')
        self.assertTrue(ret)
        ret = Experiment.validate_kpi('boston')
        self.assertTrue(ret)
        ret = Experiment.validate_kpi('1_not-two-times-two-times')
        self.assertTrue(ret)

    def test_invalid_kpi(self):
        ret = Experiment.validate_kpi('!hello-jose')
        self.assertFalse(ret)
        ret = Experiment.validate_kpi('thunder storm')
        self.assertFalse(ret)
        ret = Experiment.validate_kpi('&!&&!&')
        self.assertFalse(ret)

    def test_set_kpi(self):
        exp = Experiment.find_or_create('multi-kpi', ['kpi', '123'], redis=self.redis)
        # We shouldn't be able to manually set a KPI. Only via web request
        with self.assertRaises(ValueError):
            exp.set_kpi('bananza')

        # simulate conversion via webrequest
        client = Client(100, redis=self.redis)

        exp.get_alternative(client)
        exp.convert(client, None, 'bananza')

        exp2 = Experiment.find_or_create('multi-kpi', ['kpi', '123'], redis=self.redis)
        self.assertEqual(exp2.kpi, None)
        exp2.set_kpi('bananza')
        self.assertEqual(exp2.kpi, 'bananza')

    def test_add_kpi(self):
        exp = Experiment.find_or_create('multi-kpi-add', ['asdf', '999'], redis=self.redis)
        kpi = 'omg-pop'

        exp.add_kpi(kpi)
        key = "{0}:kpis".format(exp.key(include_kpi=False))
        self.assertIn(kpi, self.redis.smembers(key))
        exp.delete()

    def test_kpis(self):
        exp = Experiment.find_or_create('multi-kpi-add', ['asdf', '999'], redis=self.redis)
        kpis = ['omg-pop', 'zynga']

        exp.add_kpi(kpis[0])
        exp.add_kpi(kpis[1])
        ekpi = exp.kpis
        self.assertIn(kpis[0], ekpi)
        self.assertIn(kpis[1], ekpi)
        exp.delete()

    def test_excluded_clients(self):
        e = Experiment.find_or_create('count-excluded-clients', ['red', 'blue'], redis=self.redis)

        for i in range(10):
            c = Client("c-%d" % i, self.redis)
            e.exclude_client(c)

            # there is a very small chance that a client was not excluded.
            self.assertEqual(e.excluded_clients(), i + 1)

    def test_excluded_client(self):
        # need proper redis to register the msetbit script
        import sixpack.db
        sixpack.db.REDIS.flushall()
        e = Experiment.find_or_create('excluded-client', ['option-a', 'option-b'], redis=sixpack.db.REDIS)
        self.assertEqual(e.control.participant_count(), 0)
        self.assertEqual(e.control.completed_count(), 0)

        # force participate 1 proper client on the control alternative
        cnil = Client("cnil", redis=sixpack.db.REDIS)
        e.control.record_participation(cnil)
        e.convert(cnil)

        # exclude client, gets control alternative & try to convert
        c = Client("c", redis=sixpack.db.REDIS)
        e.exclude_client(c)

        self.assertTrue(e.control == e.get_alternative(c))
        self.assertTrue(None == e.existing_alternative(c))
        with self.assertRaises(ValueError):
            e.convert(c)

        # participation & completed count should be 1
        self.assertEqual(e.control.participant_count(), 1)
        self.assertEqual(e.control.completed_count(), 1)

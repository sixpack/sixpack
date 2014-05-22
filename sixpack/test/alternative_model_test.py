import unittest
import fakeredis

from sixpack.models import Alternative, Experiment


class TestAlternativeModel(unittest.TestCase):

    unit = True

    def setUp(self):
        self.redis = fakeredis.FakeStrictRedis()
        self.client_id = 381

    def test_key(self):
        exp = Experiment('show-something', ['yes', 'no'], redis=self.redis)

        alt = Alternative('yes', exp, redis=self.redis)
        key = alt.key()
        self.assertEqual(key, 'sxp:show-something:yes')

    def test_is_valid(self):
        valid = Alternative.is_valid('1')
        self.assertTrue(valid)

        unicode_valid = Alternative.is_valid(u'valid')
        self.assertTrue(unicode_valid)

    def test_is_not_valid(self):
        not_valid = Alternative.is_valid(1)
        self.assertFalse(not_valid)

        not_valid = Alternative.is_valid(':123:name')
        self.assertFalse(not_valid)

        not_valid = Alternative.is_valid('_123name')
        self.assertFalse(not_valid)

        not_valid = Alternative.is_valid('&123name')
        self.assertFalse(not_valid)

    def test_is_control(self):
        exp = Experiment('trololo', ['yes', 'no'], redis=self.redis)
        exp.save()

        alt = Alternative('yes', exp, redis=self.redis)
        self.assertTrue(alt.is_control())
        exp.delete()

    def test_experiment(self):
        exp = Experiment('trololo', ['yes', 'no'], redis=self.redis)
        exp.save()

        alt = Alternative('yes', exp, redis=self.redis)
        self.assertTrue(alt.is_control())

    def test_participant_count(self):
        pass
        # self.redis.bitcount.return_value = 0

        # alt = Alternative('yes', 'show-something', self.redis)
        # count = alt.participant_count()

        # key = _key("participation:{0}:{1}".format(alt.experiment_name, alt.name))
        # self.redis.bitcount.assert_called_once_with(key)
        # self.assertTrue(isinstance(count, Number))

        # self.redis.reset_mock()

    def test_conversion_count(self):
        pass
        # self.redis.reset_mock()
        # self.redis.bitcount.return_value = 0

        # alt = Alternative('yes', 'show-something', self.redis)
        # count = alt.completed_count()

        # key = _key("c:{0}/1:{1}".format(alt.experiment_name, alt.name))
        # self.redis.bitcount.assert_called_once_with(key)
        # self.assertTrue(isinstance(count, Number))

        # self.redis.reset_mock()

    # TODO Test this
    def test_record_participation(self):
        pass
        # alt = Alternative('yes', 'show-something', self.redis)
        # alt.record_participation(self.client_id)

        # key = _key("participation:{0}:{1}".format(alt.experiment_name, alt.name))
        # self.redis.setbit.assert_called_once_with(key, self.client_id, 1)

    def test_record_conversion(self):
        pass
        # client = Client('xyz', self.redis)
        # alt = Alternative('yes', 'show-something', self.redis)
        # alt.record_conversion(client)

        # key = _key("conversion:{0}:{1}".format(alt.experiment_name, alt.name))
        # self.redis.setbit.assert_called_once_with(key, self.client_id, 1)

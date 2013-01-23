import unittest
from numbers import Number
from mock import MagicMock
from sixpack.db import REDIS, _key

from sixpack.models import Alternative

class TestAlternativeModel(unittest.TestCase):

    unit = True

    def setUp(self):
        self.redis = MagicMock(REDIS)
        self.client_id = 381

    def test_key(self):
        alt = Alternative('yes', 'show-something', self.redis)
        key = alt.key()
        self.assertEqual(key, 'sixpack:show-something:yes')

    def test_is_valid(self):
        not_valid = Alternative.is_valid(1)
        self.assertFalse(not_valid)

        valid = Alternative.is_valid('1')
        self.assertTrue(valid)

        unicode_valid = Alternative.is_valid(u'valid')
        self.assertTrue(unicode_valid)

    def test_reset(self):
        alt = Alternative('yes', 'show-something', self.redis)
        alt.reset()
        self.redis.hset.assert_any_call(alt.key(), 'participant_count', 0)
        self.redis.hset.assert_any_call(alt.key(), 'completed_count', 0)

    def test_delete(self):
        alt = Alternative('yes', 'show-something', self.redis)
        alt.delete()
        self.redis.delete.assert_called_once_with(alt.key())

    def test_is_control(self):
        pass

    def test_experiment(self):
        pass

    def test_participant_count(self):
        self.redis.bitcount.return_value = 1

        alt = Alternative('yes', 'show-something', self.redis)
        count = alt.participant_count()

        self.redis.bitcount.assert_called_once_with(_key("participation:show-something:yes"))
        self.assertTrue(isinstance(count, Number))

        self.redis.reset_mock()

    def test_completion_count(self):
        self.redis.bitcount.return_value = 1

        alt = Alternative('yes', 'show-something', self.redis)
        count = alt.completed_count()

        self.redis.bitcount.assert_called_once_with(_key("conversion:show-something:yes"))
        self.assertTrue(isinstance(count, Number))

        self.redis.reset_mock()

    def test_record_participation(self):
        alt = Alternative('yes', 'show-something', self.redis)
        alt.record_participation(self.client_id)


    def test_record_conversion(self):
        alt = Alternative('yes', 'show-something', self.redis)
        alt.record_conversion(self.client_id)
        self.redis.setbit.assert_called_once_with(_key('conversion:show-something:yes'), 381, 1)

import unittest

from sixpack.models import Alternative

class TestAlternativeModel(unittest.TestCase):

    unit = True

    def test_key(self):
        alt = Alternative('yes', 'show-something')
        key = alt.key()
        self.assertEqual(key, 'sixpack:show-something:yes')

    def test_is_valid(self):
        not_valid = Alternative.is_valid(1)
        self.assertFalse(not_valid)

        valid = Alternative.is_valid('1')
        self.assertTrue(valid)

        unicode_valid = Alternative.is_valid(u'valid')
        self.assertTrue(unicode_valid)

    def test_increment_completion(self):
        self.assertTrue(True)
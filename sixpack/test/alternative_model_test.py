import unittest

from sixpack.models import Alternative

class TestAlternativeModel(unittest.TestCase):

    unit = True

    def test_key(self):
        alt = Alternative('yes', 'show-something')
        key = alt.key()
        self.assertEqual(key, 'sixpack:show-something:yes')
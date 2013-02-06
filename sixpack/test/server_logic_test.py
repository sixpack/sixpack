import unittest
from sixpack.server import is_robot


class TestServerLogic(unittest.TestCase):

    unit = True

    def test_is_robot(self):
        ret = is_robot('fetch')
        self.assertTrue(ret)

    def test_is_not_robot(self):
        ret = is_robot('Mozilla%2F5.0%20(Macintosh%3B%20Intel%20Mac%20OS%20X%2010_8_2)%20AppleWebKit%2F537.22%20(KHTML%2C%20like%20Gecko)%20Chrome%2F25.0.1364.45%20Safari%2F537.22')
        self.assertFalse(ret)

        ret = is_robot(None)
        self.assertFalse(ret)

import unittest
from sixpack import utils
from sixpack import metrics


class TestServerLogic(unittest.TestCase):

    unit = True

    def test_number_to_percent(self):
        number = utils.number_to_percent(0.09)
        self.assertEqual(number, '9.00%')

        number = utils.number_to_percent(0.001)
        self.assertEqual(number, '0.10%')

    def test_number_format(self):
        number = utils.number_format(100)
        self.assertEqual(number, '100')

        number = utils.number_format(1000)
        self.assertEqual(number, '1,000')

        number = utils.number_format(1234567890)
        self.assertEqual(number, '1,234,567,890')

    def test_str_to_bool(self):
        self.assertTrue(utils.to_bool('y'))
        self.assertTrue(utils.to_bool('YES'))
        self.assertTrue(utils.to_bool('true'))
        self.assertTrue(utils.to_bool('TRUE'))
        self.assertTrue(utils.to_bool('Y'))
        self.assertFalse(utils.to_bool('rodger'))
        self.assertFalse(utils.to_bool('False'))
        self.assertFalse(utils.to_bool('FaLse'))
        self.assertFalse(utils.to_bool('no'))
        self.assertFalse(utils.to_bool('n'))



class TestStatsd(unittest.TestCase):

    def test_parse_url(self):
        self.assertEqual(
            ('example.com', 9999, 'prefix'),
            metrics.parse_url('udp://example.com:9999/prefix'))

    def test_parse_url_defaults(self):
        self.assertEqual(
            ('localhost', 8125, 'sixpack'),
            metrics.parse_url(''))

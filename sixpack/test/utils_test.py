import unittest
from sixpack import utils


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

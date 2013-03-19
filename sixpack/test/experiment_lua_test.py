import unittest
import json

from sixpack.server import create_app
from sixpack.models import Client, Experiment


class TestExperimentLua(unittest.TestCase):

    def setUp(self):
        self.app = create_app()

    def test_convert(self):
        exp = Experiment('test-convert', ['1', '2'], self.app.redis)
        client = Client("eric", self.app.redis)
        exp.get_alternative(client)
        exp.convert(client)

        self.assertEqual(exp.total_conversions(), 1)
    
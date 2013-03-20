import unittest
import json

import dateutil.parser

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

    def test_cant_convert_twice(self):
        exp = Experiment('test-convert', ['1', '2'], self.app.redis)
        client = Client("eric", self.app.redis)
        alt = exp.get_alternative(client)
        exp.convert(client)
        self.assertEqual(exp.total_conversions(), 1)

        exp.convert(client, dt=dateutil.parser.parse("2012-01-01"))
        self.assertEqual(exp.total_conversions(), 1)
        data = exp.objectify_by_period("day")
        altdata = [a for a in data["alternatives"] if a["name"] == alt.name][0]["data"]
        total_participations = sum([d["participations"] for d in altdata])
        self.assertEqual(total_participations, 1)
        total_conversions = sum([d["conversions"] for d in altdata])
        self.assertEqual(total_conversions, 1)

import unittest
import json

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from sixpack.server import create_app
from sixpack.models import Experiment


class TestAlternativeChoice(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = Client(self.app, BaseResponse)

    def test_bots_get_winner_otherwise_control(self):
        e = Experiment.find_or_create("bots-get-winner", ["one", "two"], redis=self.app.redis)
        # control at first
        for i in range(3):
            data = json.loads(self.client.get("/participate?experiment=bots-get-winner&alternatives=one&alternatives=two&user_agent=GoogleBot&client_id=rand").data)
            self.assertEqual(data['alternative']['name'], 'one')
        # winner once one is set
        e.set_winner("two")
        for i in range(3):
            data = json.loads(self.client.get("/participate?experiment=bots-get-winner&alternatives=one&alternatives=two&user_agent=GoogleBot&client_id=rand").data)
            self.assertEqual(data['alternative']['name'], 'two')

    def test_force_param_always_wins(self):
        alts = ["one", "two", "three"]
        e = Experiment.find_or_create("force-param-always-wins", alts, redis=self.app.redis)

        def test_force():
            for f in alts:
                data = json.loads(self.client.get("/participate?experiment=force-param-always-wins&alternatives=one&alternatives=two&alternatives=three&client_id=rand&force={0}".format(f)).data)
                self.assertEqual(data['alternative']['name'], f)
        # before a winner
        test_force()
        e.set_winner("three")
        # after a winner
        test_force()

    def test_client_chosen_alternative(self):
        alts = ["one", "two", "three"]
        e = Experiment.find_or_create("client-chosen-alternative", alts, redis=self.app.redis)

        data = json.loads(self.client.get("/participate?experiment=client-chosen-alternative&alternatives=one&alternatives=two&alternatives=three&client_id=1&alternative=one").data)
        self.assertEqual(data['alternative']['name'], 'one')
        self.assertEqual(e.total_participants(), 1)

        data = json.loads(self.client.get("/participate?experiment=client-chosen-alternative&alternatives=one&alternatives=two&alternatives=three&client_id=2&alternative=two").data)
        self.assertEqual(data['alternative']['name'], 'two')
        self.assertEqual(e.total_participants(), 2)

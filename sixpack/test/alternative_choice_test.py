import unittest
import json

import fakeredis
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from sixpack.server import create_app
from sixpack.models import Experiment
from sixpack.models import Client as SClient

class TestAlternativeChoice(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = Client(self.app, BaseResponse)
        self.redis = fakeredis.FakeStrictRedis()

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

    def test_uniform_choice(self):

        # test name: deterministic-1
        # client: 09a7407c-e371-492b-82e3-ef438d960ca3
        # num alts: 2
        # salted: deterministic-1.09a7407c-e371-492b-82e3-ef438d960ca3
        # hased: 179d8fdfcd3b4725a112121af37620cca633fbdc
        # first 7: 179d8fd
        # to int: 24762621
        # mod 2: 1
        exp = Experiment('deterministic-1', ['y', 'n'], redis=self.redis)
        cli = SClient('09a7407c-e371-492b-82e3-ef438d960ca3', redis=self.redis)
        alt = exp.get_alternative(cli).name
        self.assertEqual('n', alt)

        # test name: deterministic-1
        # client: 09a7407c-e371-492b-82e3-ef438d960ca3
        # num alts: 3
        # salted: deterministic-1.09a7407c-e371-492b-82e3-ef438d960ca3
        # hased: 179d8fdfcd3b4725a112121af37620cca633fbdc
        # first 7: 179d8fd
        # to int: 24762621
        # mod 3: 1
        exp = Experiment('deterministic-1', ['y', 'n', 'm'], redis=self.redis)
        cli = SClient('09a7407c-e371-492b-82e3-ef438d960ca3', redis=self.redis)
        alt = exp.get_alternative(cli).name
        self.assertEqual('n', alt)

        # test name: deterministic-2
        # client: 1b7b8b69-9b5b-4720-ba08-3e449fd60260
        # num alts: 3
        # salted: deterministic-2.1b7b8b69-9b5b-4720-ba08-3e449fd60260
        # hased: c55c5f029437e37ba830c18810362a3ffaa31538
        # first 7: c55c5f0
        # to int: 206947824
        # mod 3: 0
        exp = Experiment('deterministic-2', ['y', 'n', 'm'], redis=self.redis)
        cli = SClient('1b7b8b69-9b5b-4720-ba08-3e449fd60260', redis=self.redis)
        alt = exp.get_alternative(cli).name
        self.assertEqual('y', alt)

        # test name: deterministic-3
        # client: 53c07ed4-80cd-4860-ad68-7eb76ed27180
        # num alts: 6
        # salted: deterministic-3.53c07ed4-80cd-4860-ad68-7eb76ed27180
        # hased: d802aac8271a522eac4ad596967a5bf3e5696a72
        # first 7: d802aac
        # to int: 226503340
        # mod 6: 4
        exp = Experiment('deterministic-3', ['y', 'n', 'm', 'one', 'two', 'three'], redis=self.redis)
        cli = SClient('53c07ed4-80cd-4860-ad68-7eb76ed27180', redis=self.redis)
        alt = exp.get_alternative(cli).name
        self.assertEqual('two', alt)

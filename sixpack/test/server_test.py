import unittest

import fakeredis
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from sixpack.server import Sixpack


class TestServer(unittest.TestCase):

    def setUp(self):
        self.redis = fakeredis.FakeStrictRedis()
        self.app = Sixpack(self.redis)
        self.client = Client(self.app, BaseResponse)

    def base_test(self):
        self.assertEqual(200, self.client.get("/").status_code)



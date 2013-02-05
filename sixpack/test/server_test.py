import unittest

import fakeredis
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from sixpack.server import (create_app,
                            Sixpack)


class TestServer(unittest.TestCase):

    def setUp(self):
        # tried using fakeredis here but it barfed on scripts
        self.app = create_app()
        self.client = Client(self.app, BaseResponse)

    def test_base(self):
        self.assertEqual(200, self.client.get("/").status_code)

    def test_sans_callback(self):
        res = self.client.get("/participate?experiment=dummy&client_id=foo&alternatives=one&alternatives=two")
        self.assertEqual(200, res.status_code)
        self.assertEqual("application/json", dict(res.headers)["Content-Type"])
        self.assert_(res.data.startswith("{"))
        self.assert_(res.data.endswith("}"))

    def test_with_callback(self):
        res = self.client.get("/participate?experiment=dummy&client_id=foo&alternatives=one&alternatives=two&callback=seatgeek.cb")
        self.assertEqual(200, res.status_code)
        self.assertEqual("application/javascript", dict(res.headers)["Content-Type"])
        self.assert_(res.data.startswith("foo({"))
        self.assert_(res.data.endswith("})"))

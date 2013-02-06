import unittest
import json

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from sixpack.server import create_app

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
        self.assert_(res.data.startswith("seatgeek.cb({"))
        self.assert_(res.data.endswith("})"))

    def test_with_bad_callback(self):
        # TODO error out here instead?
        res = self.client.get("/participate?experiment=dummy&client_id=foo&alternatives=one&alternatives=two&callback=alert();foo")
        self.assertEqual(200, res.status_code)
        self.assertEqual("application/json", dict(res.headers)["Content-Type"])
        self.assert_(res.data.startswith("{"))
        self.assert_(res.data.endswith("}"))

    def test_ok_participate(self):
        resp = self.client.get("/participate?experiment=dummy&client_id=foo&alternatives=one&alternatives=two")
        data = json.loads(resp.data )
        self.assertEqual(200, resp.status_code)
        self.assertTrue('alternative' in data)
        self.assertTrue('experiment' in data)
        self.assertTrue('client_id' in data)
        self.assertTrue('status' in data)
        self.assertEqual(data['status'], 'ok')

    def test_useragent_filter(self):
        resp = self.client.get("/participate?experiment=dummy&client_id=foo&alternatives=one&alternatives=two&user_agent=fetch")
        data = json.loads(resp.data )
        self.assertEqual(200, resp.status_code)
        self.assertTrue('alternative' in data)
        self.assertFalse('experiment' in data)
        self.assertFalse('client_id' in data)
        self.assertFalse('status' in data)

    def test_convert(self):
        resp = self.client.get("/convert?experiment=dummy&client_id=foo")
        data = json.loads(resp.data )
        self.assertEqual(200, resp.status_code)
        self.assertTrue('status' in data)
        self.assertEqual(data['status'], 'ok')

    def test_convert_fail(self):
        resp = self.client.get("/convert?experiment=baz&client_id=bar")
        data = json.loads(resp.data )
        self.assertEqual(400, resp.status_code)
        self.assertTrue('status' in data)
        self.assertEqual(data['status'], 'failure')

    def test_client_id(self):
        resp = self.client.get("/participate?experiment=dummy&alternatives=one&alternatives=two")
        data = json.loads(resp.data)
        self.assertEqual(400, resp.status_code)
        self.assertTrue('status' in data)
        self.assertEqual(data['status'], 'missing arguments')
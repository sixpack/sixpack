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

    def test_status(self):
        res = self.client.get("/_status")
        data = json.loads(res.data)
        self.assertEqual(200, res.status_code)
        self.assertTrue('status' in data)
        self.assertEqual('ok', data['status'])

    def test_404(self):
        res = self.client.get("/i-would-walk-five-thousand-miles")
        data = json.loads(res.data)
        self.assertEqual(404, res.status_code)
        self.assertTrue('message' in data)
        self.assertEqual('not found', data['message'])
        self.assertTrue('status' in data)
        self.assertEqual('failed', data['status'])

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
        data = json.loads(resp.data)
        self.assertEqual(200, resp.status_code)
        self.assertTrue('alternative' in data)
        self.assertTrue('name' in data['alternative'])
        self.assertTrue('experiment' in data)
        self.assertTrue('name' in data['experiment'])
        self.assertTrue('client_id' in data)
        self.assertTrue('status' in data)
        self.assertEqual(data['status'], 'ok')

    def test_participate_useragent_filter(self):
        resp = self.client.get("/participate?experiment=dummy&client_id=foo&alternatives=one&alternatives=two&user_agent=fetch")
        data = json.loads(resp.data)
        self.assertEqual(200, resp.status_code)
        self.assertTrue('alternative' in data)
        self.assertTrue('experiment' in data)
        self.assertTrue('client_id' in data)
        self.assertTrue('status' in data)

    def test_convert_useragent_filter(self):
        resp = self.client.get("/convert?experiment=dummy&client_id=foo&user_agent=fetch")
        data = json.loads(resp.data)
        self.assertEqual(200, resp.status_code)
        self.assertTrue('status' in data)
        self.assertTrue('excluded' in data)
        self.assertEqual('true', data['excluded'])

    def test_convert(self):
        self.client.get("/participate?experiment=dummy&client_id=foo&alternatives=one&alternatives=two&callback=seatgeek.cb")
        resp = self.client.get("/convert?experiment=dummy&client_id=foo")
        data = json.loads(resp.data)
        self.assertEqual(200, resp.status_code)
        self.assertTrue('status' in data)
        self.assertEqual(data['status'], 'ok')
        self.assertTrue('alternative' in data)
        self.assertTrue('name' in data['alternative'])
        self.assertTrue('experiment' in data)
        self.assertTrue('name' in data['experiment'])
        self.assertTrue('client_id' in data)
        self.assertTrue('conversion' in data)
        self.assertTrue('value' in data['conversion'])
        self.assertTrue('kpi' in data['conversion'])
        self.assertEqual(data['conversion']['kpi'], None)

    def test_convert_with_kpi(self):
        self.client.get("/participate?experiment=dummy-kpi&client_id=foo&alternatives=one&alternatives=two")
        resp = self.client.get("/convert?experiment=dummy-kpi&client_id=foo&kpi=alligator")
        data = json.loads(resp.data)
        self.assertEqual(200, resp.status_code)
        self.assertTrue('status' in data)
        self.assertEqual(data['status'], 'ok')
        self.assertTrue('alternative' in data)
        self.assertTrue('name' in data['alternative'])
        self.assertTrue('experiment' in data)
        self.assertTrue('name' in data['experiment'])
        self.assertTrue('client_id' in data)
        self.assertTrue('conversion' in data)
        self.assertTrue('value' in data['conversion'])
        self.assertTrue('kpi' in data['conversion'])
        self.assertEqual(data['conversion']['kpi'], 'alligator')

    def test_convert_bad_kpi_failure(self):
        self.client.get("/participate?experiment=dummy-kpi&client_id=foo&alternatives=one&alternatives=two")
        resp = self.client.get("/convert?experiment=dummy-kpi&client_id=foo&kpi=&&^^!*(")
        data = json.loads(resp.data)
        self.assertEqual(400, resp.status_code)
        self.assertTrue('status' in data)
        self.assertEqual(data['message'], 'invalid kpi name')
        self.assertEqual(data['status'], 'failed')

    def test_convert_fail(self):
        resp = self.client.get("/convert?experiment=baz&client_id=bar")
        data = json.loads(resp.data)
        self.assertEqual(400, resp.status_code)
        self.assertTrue('status' in data)
        self.assertEqual(data['status'], 'failed')
        self.assertEqual(data['message'], 'experiment does not exist')

    def test_client_id(self):
        resp = self.client.get("/participate?experiment=dummy&alternatives=one&alternatives=two")
        data = json.loads(resp.data)
        self.assertEqual(400, resp.status_code)
        self.assertTrue('status' in data)
        self.assertEqual(data['status'], 'failed')
        self.assertEqual(data['message'], 'missing arguments')

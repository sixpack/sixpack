import unittest
import statsd
from mock import patch, call

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from sixpack.config import CONFIG as cfg
from sixpack.server import create_app


class TestServer(unittest.TestCase):

    @patch('sixpack.metrics.StatsClient', spec=statsd.StatsClient)
    def setUp(self, statsd_client):
        cfg['metrics'] = True
        self.app = create_app()
        self.client = Client(self.app, BaseResponse)

    def assertMetrics(self, response_code, endpoint):
        self.assertEqual(
            [call('{}.count'.format(endpoint)),
             call('response_code.{}'.format(response_code))],
            self.app.statsd.incr.call_args_list)
        self.app.statsd.timer.assert_called_once_with('{}.response_time'.format(endpoint))

    def test_base(self):
        self.assertEqual(200, self.client.get("/").status_code)
        self.assertMetrics(200, 'home')

    def test_404(self):
        res = self.client.get("/i-would-walk-five-thousand-miles")
        self.assertEqual(404, res.status_code)
        self.app.statsd.incr.assert_called_once_with('response_code.404')

    def test_participate_bad_params(self):
        resp = self.client.get("/participate")
        self.assertEqual(400, resp.status_code)
        self.assertMetrics(400, 'participate')

    def test_participate_ok(self):
        resp = self.client.get("/participate?experiment=dummy&client_id=foo&alternatives=one&alternatives=two")
        self.assertEqual(200, resp.status_code)
        self.assertMetrics(200, 'participate')

    def test_convert_bad_params(self):
        resp = self.client.get("/convert")
        self.assertEqual(400, resp.status_code)
        self.assertMetrics(400, 'convert')

    def test_convert_ok(self):
        self.client.get("/participate?experiment=dummy&client_id=foo&alternatives=one&alternatives=two")
        self.app.statsd.reset_mock()
        resp = self.client.get("/convert?experiment=dummy&client_id=foo")
        self.assertEqual(200, resp.status_code)
        self.assertMetrics(200, 'convert')

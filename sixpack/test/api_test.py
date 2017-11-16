import unittest
from mock import patch, Mock

import sixpack
from sixpack.models import Experiment, Alternative
from sixpack.api import participate, convert

import fakeredis

class TestApi(unittest.TestCase):

    @patch.object(Experiment, "find_or_create")
    def test_participate(self, mock_find_or_create):
        exp = Experiment("test", ["no", "yes"], winner=None)
        exp.get_alternative = Mock(return_value=Alternative("yes", exp))
        mock_find_or_create.return_value = exp
        alternative = participate("test", ["no", "yes"], "id1")
        self.assertEqual("yes", alternative.name)
        self.assertEqual("test", alternative.experiment.name)

    @patch.object(Experiment, "find_or_create")
    def test_participate_with_forced_alternative(self, mock_find_or_create):
        mock_find_or_create.return_value = Experiment("test", ["no", "yes"], winner=None)
        alternative = participate("test", ["no", "yes"], "id1", force="yes")
        self.assertEqual("yes", alternative.name)

    @patch.object(Experiment, "find_or_create")
    def test_participate_with_forced_and_record_force_alternative(self, mock_find_or_create):
        mock_find_or_create.return_value = Experiment("test", ["no", "yes"], winner=None)
        alternative = participate("test", ["no", "yes"], "id1", force="yes", record_force=True, redis=fakeredis.FakeStrictRedis())
        self.assertEqual("yes", alternative.name)
        self.assertEqual("test", alternative.experiment.name)

    @patch.object(Experiment, "find")
    def test_convert(self, mock_find):
        exp = Experiment("test", ["no", "yes"], winner=None)
        exp.convert = Mock(return_value=Alternative("yes", exp))
        mock_find.return_value = exp
        alternative = convert("test", "id1")
        self.assertEqual("yes", alternative.name)
        self.assertEqual("test", alternative.experiment.name)

    @patch.object(Experiment, "find")
    def test_convert_with_kpi(self, mock_find):
        exp = Experiment("test", ["no", "yes"], winner=None)
        exp.convert = Mock(return_value=Alternative("yes", exp))
        mock_find.return_value = exp
        alternative = convert("test", "id1", kpi="goal1")
        # TODO: we're not really asserting anything about the KPI
        self.assertEqual("yes", alternative.name)
        self.assertEqual("test", alternative.experiment.name)

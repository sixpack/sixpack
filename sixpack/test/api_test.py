import unittest
from mock import patch, Mock

import sixpack
from sixpack.models import Experiment, Alternative
from sixpack.api import participate, convert


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

    @patch.object(Alternative, "record_participation")
    @patch.object(Experiment, "find_or_create")
    def test_participate_with_bucket(self, mock_find_or_create, mock_record_participation):
        exp = Experiment("test", ["no", "yes"], winner=None)
        exp.is_archived = Mock(return_value=False)
        exp.existing_alternative = Mock(return_value=False)
        mock_find_or_create.return_value = exp

        mock_record_participation.return_value = Alternative("no", exp)

        alternative = participate("test", ["no", "yes"], "id1", bucket="no")
        self.assertEqual("no", alternative.name)

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

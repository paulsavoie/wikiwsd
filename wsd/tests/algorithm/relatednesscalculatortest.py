import unittest
import math
from wsd.algorithm import RelatednessCalculator
from wsd.tests.database.databasemocks import *

class RelatednessCalculatorTest(unittest.TestCase):
    def setUp(self):
        self._work_view = WorkViewMock()
        self._calculator = RelatednessCalculator(self._work_view)

    def _calculate_relatedness(self, id1, articleincount1, id2, articleincount2):
        article1 = {
            'id': id1,
            'title': 'Dummy Article 1',
            'text': '',
            'links': [],
            'articleincount': articleincount1
        }
        article2 = {
            'id': id2,
            'title': 'Dummy Article 1',
            'text': '',
            'links': [],
            'articleincount': articleincount2
        }
        return self._calculator.calculate_relatedness(article1, article2)

    def test_simple(self):
        self._work_view.commons.append({
            'id1': 1, 'id2': 2, 'num': 3
        })
        result = self._calculate_relatedness(1, 100, 2, 50)
        expected = (math.log(100.0) - math.log(3.0)) / (math.log(4696033.0) - math.log(50.0))
        self.assertEqual(result, expected)
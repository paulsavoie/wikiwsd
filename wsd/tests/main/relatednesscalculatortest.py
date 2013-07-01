import unittest
import math
from wsd.relatednesscalculator import RelatednessCalculator 

class RelatednessCalculatorTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_simple(self):
        retriever = MockCommonnessRetriever()
        retriever.commons = [
            { 'id1': 1, 'id2': 2, 'num': 3 }
        ]

        calculator = RelatednessCalculator(retriever)
        result = calculator.calculate_relatedness({ 'id': 1, 'articleincount': 100 }, { 'id': 2, 'articleincount': 50 })

        expected = (math.log(100.0) - math.log(3.0)) / (math.log(4696033.0) - math.log(50.0))

        self.assertEqual(retriever.called, 1)
        self.assertEqual(result, expected)

class MockCommonnessRetriever():
    def __init__(self):
        self.commons = []
        self.called = 0

    def retrieve_commonness(self, article1, article2):
        self.called += 1
        for common in self.commons:
            if (article1['id'] == common['id1'] and article2['id'] == common['id2']) or (article1['id'] == common['id2'] and article2['id'] == common['id1']):
                return common['num']
        return 0
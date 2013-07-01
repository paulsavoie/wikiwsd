import unittest
from wsd.decider import Decider 

class DeciderTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_single_noun(self):
        calculator = MockRelatednessCalculator()
        terms = [
            { 'isNoun': True, 'token': 'book', 'id': 555, 'disambiguations': [
                { 'id': 1, 'percentage': 0.9, 'meaning': 'meaning1' },
                { 'id': 2, 'percentage': 0.1, 'meaning': 'meaning2' }
            ] }
        ]

        decider = Decider(calculator)
        decider.decide(terms)

        self.assertEqual(calculator.called, 0)
        self.assertEqual(terms[0]['finalIndex'], 0)

    def test_no_meanings(self):
        calculator = MockRelatednessCalculator()
        terms = [
            { 'isNoun': True, 'token': 'book', 'id': 555, 'disambiguations': [] }
        ]

        decider = Decider(calculator)
        decider.decide(terms)

        self.assertEqual(calculator.called, 0)
        self.assertEqual(terms[0]['finalIndex'], -1)

    def test_correlation(self):
        calculator = MockRelatednessCalculator()
        calculator.commons = [
            { 'id1': 2, 'id2': 4, 'num': 0.98 },
            { 'id1': 2, 'id2': 3, 'num': 0.001 }
        ]
        terms = [
            { 'isNoun': True, 'token': 'book', 'id': 555, 'disambiguations': [
                { 'id': 1, 'percentage': 0.9, 'meaning': 'meaning1' },
                { 'id': 2, 'percentage': 0.1, 'meaning': 'meaning2' }
            ] }, { 'isNoun': True, 'token': 'cars', 'id': 556, 'disambiguations': [
                { 'id': 3, 'percentage': 0.9, 'meaning': 'meaning1' },
                { 'id': 4, 'percentage': 0.1, 'meaning': 'meaning2' }
            ] }
        ]

        decider = Decider(calculator)
        decider.decide(terms)

        self.assertEqual(calculator.called, 6)
        self.assertEqual(terms[0]['finalIndex'], 1)
        self.assertEqual(terms[1]['finalIndex'], 1)

    def test_limited_correlation(self):
        calculator = MockRelatednessCalculator()
        calculator.commons = [
            { 'id1': 2, 'id2': 16, 'num': 0.99} # will be ignored because it is too far off position of first
        ]
        terms = [
            { 'isNoun': True, 'token': 'term1', 'id': 555, 'disambiguations': [
                { 'id': 1, 'percentage': 0.1, 'meaning': 'meaning1' },
                { 'id': 2, 'percentage': 0.1, 'meaning': 'meaning2' }
            ] }, { 'isNoun': True, 'token': 'term2', 'id': 556, 'disambiguations': [
                { 'id': 3, 'percentage': 0.1, 'meaning': 'meaning1' },
                { 'id': 4, 'percentage': 0.1, 'meaning': 'meaning2' }
            ] }, { 'isNoun': True, 'token': 'term3', 'id': 557, 'disambiguations': [
                { 'id': 5, 'percentage': 0.1, 'meaning': 'meaning1' },
                { 'id': 6, 'percentage': 0.1, 'meaning': 'meaning2' }
            ] }, { 'isNoun': True, 'token': 'term4', 'id': 558, 'disambiguations': [
                { 'id': 7, 'percentage': 0.1, 'meaning': 'meaning1' },
                { 'id': 8, 'percentage': 0.1, 'meaning': 'meaning2' }
            ] }, { 'isNoun': True, 'token': 'term5', 'id': 559, 'disambiguations': [
                { 'id': 9, 'percentage': 0.1, 'meaning': 'meaning1' },
                { 'id': 10, 'percentage': 0.1, 'meaning': 'meaning2' }
            ] }, { 'isNoun': True, 'token': 'term6', 'id': 560, 'disambiguations': [
                { 'id': 11, 'percentage': 0.1, 'meaning': 'meaning1' },
                { 'id': 12, 'percentage': 0.1, 'meaning': 'meaning2' }
            ] }, { 'isNoun': True, 'token': 'term7', 'id': 561, 'disambiguations': [
                { 'id': 13, 'percentage': 0.1, 'meaning': 'meaning1' },
                { 'id': 14, 'percentage': 0.1, 'meaning': 'meaning2' }
            ] }, { 'isNoun': True, 'token': 'term8', 'id': 561, 'disambiguations': [
                { 'id': 15, 'percentage': 0.1, 'meaning': 'meaning1' },
                { 'id': 16, 'percentage': 0.1, 'meaning': 'meaning2' }
            ] }
        ]

        decider = Decider(calculator)
        decider.decide(terms)

        self.assertEqual(calculator.called, 144) # = 2*12 + 2*11 + 2*10 + 2*9 + 2*9 + 2*8 + 2*7 + 2*6
        self.assertEqual(terms[0]['finalIndex'], 0)
        self.assertEqual(terms[7]['finalIndex'], 0)

class MockRelatednessCalculator():
    def __init__(self):
        self.commons = []
        self.called = 0

    def calculate_relatedness(self, article1, article2):
        self.called += 1
        for common in self.commons:
            if (article1['id'] == common['id1'] and article2['id'] == common['id2']) or (article1['id'] == common['id2'] and article2['id'] == common['id1']):
                return common['num']
        return 0.0
import unittest
from wsd.algorithm import Decider
from mockrelatednesscalculator import MockRelatednessCalculator

class DeciderTest(unittest.TestCase):
    def setUp(self):
        self._relatedness_calculator = MockRelatednessCalculator()
        self._decider = Decider(self._relatedness_calculator)

    def _decide(self, links):
        article = {
            'id': None,
            'title': None,
            'text': None,
            'links': links
        }
        self._decider.decide(article)
        return article['links']


    def test_single_link(self):
        links = [
            {
                'phrase': 'book',
                'meanings': [
                    { 'target_article_id': 1, 'commonness': 0.1, 'target_article_name': 'meaning1' },
                    { 'target_article_id': 2, 'commonness': 0.9, 'target_article_name': 'meaning2' }
                ]
            }
        ]
        result = self._decide(links)
        self.assertEqual(result[0]['meanings'][0]['target_article_id'], 2)

    def test_no_meanings(self):
        links = [
            {
                'phrase': 'book',
                'meanings':[]
            }
        ]
        result = self._decide(links)
        self.assertEqual(result[0]['meanings'], [])
    
    def test_correlation(self):
        self._relatedness_calculator.commons = [
            { 'id1': 2, 'id2': 4, 'num': 0.98 },
            { 'id1': 2, 'id2': 3, 'num': 0.001 }
        ]
        links = [
            {
                'phrase': 'book',
                    'meanings': [
                    { 'target_article_id': 1, 'commonness': 0.9, 'target_article_name': 'meaning1' },
                    { 'target_article_id': 2, 'commonness': 0.1, 'target_article_name': 'meaning2' }
                ]
            },
            {
                'phrase': 'cars',
                    'meanings': [
                    { 'target_article_id': 4, 'commonness': 0.1, 'target_article_name': 'meaning4' }
                ]
            }
        ]
        result = self._decide(links)
        self.assertEqual(result[0]['meanings'][0]['target_article_id'], 2)
        self.assertEqual(result[1]['meanings'][0]['target_article_id'], 4)

    def test_many(self):
        self._relatedness_calculator.commons = [
            { 'id1': 2, 'id2': 17, 'num': 0.99 }, # will be ignore because it is too far apart
            { 'id1': 3, 'id2':  5, 'num': 0.99 },
            { 'id1': 4, 'id2':  5, 'num': 0.01 },
            { 'id1': 2, 'id2':  7, 'num': 0.50 },
            { 'id1': 2, 'id2':  8, 'num': 0.20 },
            { 'id1': 5, 'id2': 13, 'num': 0.60 },
            { 'id1': 3, 'id2': 13, 'num': 0.80 },
            { 'id1': 5, 'id2': 12, 'num': 0.30 }
        ]
        links = [
            {
                'phrase': 'term1',
                    'meanings': [
                    { 'target_article_id':  1, 'commonness': 0.2, 'target_article_name': 'meaning01' },
                    { 'target_article_id':  2, 'commonness': 0.1, 'target_article_name': 'meaning02' } # this one ? (actually only in second iteration)
                ]
            },
            {
                'phrase': 'term2',
                    'meanings': [
                    { 'target_article_id':  3, 'commonness': 0.1, 'target_article_name': 'meaning03' }, # this one
                    { 'target_article_id':  4, 'commonness': 0.9, 'target_article_name': 'meaning04' }
                ]
            },
            {
                'phrase': 'term3',
                    'meanings': [
                    { 'target_article_id':  5, 'commonness': 0.1, 'target_article_name': 'meaning05' } # this one
                ]
            },
            {
                'phrase': 'term4',
                    'meanings': [
                    { 'target_article_id':  6, 'commonness': 0.2, 'target_article_name': 'meaning06' },
                    { 'target_article_id':  7, 'commonness': 0.4, 'target_article_name': 'meaning07' }, # this one
                    { 'target_article_id':  8, 'commonness': 0.4, 'target_article_name': 'meaning08' }
                ]
            },
            {
                'phrase': 'term5',
                    'meanings': [
                    { 'target_article_id':  9, 'commonness': 0.7, 'target_article_name': 'meaning09' }, # this one
                    { 'target_article_id': 10, 'commonness': 0.2, 'target_article_name': 'meaning10' },
                    { 'target_article_id': 11, 'commonness': 0.1, 'target_article_name': 'meaning11' }
                ]
            },
            {
                'phrase': 'term6',
                    'meanings': [
                    { 'target_article_id': 12, 'commonness': 0.7, 'target_article_name': 'meaning12' },
                    { 'target_article_id': 13, 'commonness': 0.4, 'target_article_name': 'meaning13' }, # this one
                    { 'target_article_id': 14, 'commonness': 0.2, 'target_article_name': 'meaning14' }
                ]
            },
            {
                'phrase': 'term7',
                    'meanings': [
                    { 'target_article_id': 15, 'commonness': 0.6, 'target_article_name': 'meaning15' }, # this one
                    { 'target_article_id': 16, 'commonness': 0.4, 'target_article_name': 'meaning16' }
                ]
            },
            {
                'phrase': 'term8',
                    'meanings': [
                    { 'target_article_id': 17, 'commonness': 0.6, 'target_article_name': 'meaning17' }, # this one
                    { 'target_article_id': 18, 'commonness': 0.4, 'target_article_name': 'meaning18' }
                ]
            }
        ]
        result = self._decide(links)
        self.assertEqual(result[0]['meanings'][0]['target_article_id'], 1)
        self.assertEqual(result[1]['meanings'][0]['target_article_id'], 3)
        self.assertEqual(result[2]['meanings'][0]['target_article_id'], 5)
        self.assertEqual(result[3]['meanings'][0]['target_article_id'], 7)
        self.assertEqual(result[4]['meanings'][0]['target_article_id'], 9)
        self.assertEqual(result[5]['meanings'][0]['target_article_id'], 13)
        self.assertEqual(result[6]['meanings'][0]['target_article_id'], 15)
        self.assertEqual(result[7]['meanings'][0]['target_article_id'], 17)
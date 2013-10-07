import unittest
from wsd.algorithm import MeaningFinder
from wsd.tests.database.databasemocks import *

class MeaningFinderTest(unittest.TestCase):
    def setUp(self):
        self._view = WorkViewMock()

    def _find_meanings(self, terms):
        links = []
        for term in terms:
            links.append({
                'target_article_id': None,
                'target_article_name': None,
                'phrase': term
            })
        article = {
            'id': 1,
            'title': 'myArticle',
            'text': [],
            'links': links
        }
        finder = MeaningFinder(self._view)
        finder.find_meanings(article)
        return article['links']

    def test_single_meaning(self):
        self._view.meanings['myNoun'] = [{
                'occurrences': 1,
                'name': 'meaning1',
                'id': 1,
                'articleincount': 2
            }]
        reference = {
            'commonness': 1.0,
            'target_article_name': 'meaning1',
            'target_article_id': 1,
            'articleincount': 2
        }
        links = self._find_meanings(['myNoun'])
        self.assertEqual(len(links), 1)
        self.assertEqual(len(links[0]['meanings']), 1)
        self.assertEqual(links[0]['meanings'][0], reference)

    def test_no_link(self):
        links = self._find_meanings([])
        self.assertEqual(len(links), 0)

    def test_multiple_meanings(self):
        self._view.meanings['myNoun'] = [{
                'occurrences': 1,
                'name': 'meaning1',
                'id': 1,
                'articleincount': 2
            }, {
                'occurrences': 3,
                'name': 'meaning2',
                'id': 2,
                'articleincount': 3
            }]
        reference1 = {
            'commonness': 0.25,
            'target_article_name': 'meaning1',
            'target_article_id': 1,
            'articleincount': 2
        }
        reference2 = {
            'commonness': 0.75,
            'target_article_name': 'meaning2',
            'target_article_id': 2,
            'articleincount': 3
        }
        links = self._find_meanings(['myNoun'])
        self.assertEqual(len(links), 1)
        self.assertEqual(len(links[0]['meanings']), 2)
        self.assertEqual(links[0]['meanings'][0], reference1)
        self.assertEqual(links[0]['meanings'][1], reference2)

    def test_multiple_terms(self):
        self._view.meanings['myNoun'] = [{
                'occurrences': 1,
                'name': 'meaning1',
                'id': 1,
                'articleincount': 2
            }]
        reference = {
            'commonness': 1.0,
            'target_article_name': 'meaning1',
            'target_article_id': 1,
            'articleincount': 2
        }
        links = self._find_meanings(['myNoun', 'myNoun2'])
        self.assertEqual(len(links), 2)
        self.assertEqual(len(links[0]['meanings']), 1)
        self.assertEqual(links[0]['meanings'][0], reference)
        self.assertEqual(len(links[1]['meanings']), 0)

    def test_same_term(self):
        self._view.meanings['myNoun'] = [{
                'occurrences': 1,
                'name': 'meaning1',
                'id': 1,
                'articleincount': 2
            }]
        reference = {
            'commonness': 1.0,
            'target_article_name': 'meaning1',
            'target_article_id': 1,
            'articleincount': 2
        }
        links = self._find_meanings(['myNoun', 'myNoun'])
        self.assertEqual(len(links), 2)
        self.assertEqual(len(links[0]['meanings']), 1)
        self.assertEqual(links[0]['meanings'][0], reference)
        self.assertEqual(len(links[1]['meanings']), 1)
        self.assertEqual(links[1]['meanings'][0], reference)
        self.assertEqual(self._view.query_counter, 1)
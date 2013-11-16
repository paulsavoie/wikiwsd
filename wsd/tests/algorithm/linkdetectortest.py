import unittest
from wsd.algorithm import LinkDetector
from wsd.tests.database.databasemocks import *

class LinkDetectorTest(unittest.TestCase):
    def setUp(self):
        self._view = WorkViewMock()

    def _detect_links(self, text):
        links = []
        article = {
            'id': 1,
            'title': 'myArticle',
            'text': text,
            'links': []
        }
        detector = LinkDetector(self._view)
        detector.detect_links(article)
        return article

    def test_single_link(self):
        self._view.occurrences['term'] = { 'occurrences': 7, 'as_link': 3 }
        self._view.occurrences['another'] = { 'occurrences': 100, 'as_link': 0 }

        article = self._detect_links('Here is another term.')
        self.assertEqual(article['text'], 'Here is another [[term]].')
        self.assertEqual(len(article['links']), 1)
        self.assertEqual(article['links'][0], { 'target_article_id': None, 'target_article_name': None, 'phrase': 'term' })

    def test_multiple_links(self):
        self._view.occurrences['term'] = { 'occurrences': 7, 'as_link': 3 }
        self._view.occurrences['is another'] = { 'occurrences': 100, 'as_link': 3 }

        article = self._detect_links('Here is another term.')
        self.assertEqual(article['text'], 'Here [[is another]] [[term]].')
        self.assertEqual(len(article['links']), 2)
        self.assertEqual(article['links'][0], { 'target_article_id': None, 'target_article_name': None, 'phrase': 'is another' })
        self.assertEqual(article['links'][1], { 'target_article_id': None, 'target_article_name': None, 'phrase': 'term' })

    def test_threshold(self):
        self._view.occurrences['term'] = { 'occurrences': 100000, 'as_link': 2 }

        article = self._detect_links('Here is another term.')
        self.assertEqual(article['text'], 'Here is another term.')
        self.assertEqual(len(article['links']), 0)
        
    def test_encapsulated_link(self):
        self._view.occurrences['term'] = { 'occurrences': 7, 'as_link': 3 }
        self._view.occurrences['encapsulated term'] = { 'occurrences': 10, 'as_link': 10 }

        article = self._detect_links('Here is another encapsulated term.')
        self.assertEqual(article['text'], 'Here is another [[encapsulated term]].')
        self.assertEqual(len(article['links']), 1)
        self.assertEqual(article['links'][0], { 'target_article_id': None, 'target_article_name': None, 'phrase': 'encapsulated term' })
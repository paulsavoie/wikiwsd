import unittest
import Queue
from wsd.build import ArticleInserter
from wsd.tests.database.databasemocks import *

class ArticleInserterTest(unittest.TestCase):

    def test_article(self):
        queue = Queue.Queue()
        view = BuildViewMock()
        inserter = ArticleInserter(queue, view)
        inserter.start()
        queue.put({
            'id': 1,
            'title': 'myArticle1',
            'type': 'article'
        })
        queue.put({
            'id': 2,
            'title': 'myArticle2',
            'type': 'article'
        })
        queue.join()
        inserter.end()
        inserter.join()
        self.assertEqual(len(view.articles), 2)
        self.assertEqual(view.articles[0], (1, 'myArticle1'))
        self.assertEqual(view.articles[1], (2, 'myArticle2'))
        self.assertEqual(view.commited, 2)
        self.assertEqual(view.cache_reset, 2)

    def test_redirect(self):
        queue = Queue.Queue()
        view = BuildViewMock()
        inserter = ArticleInserter(queue, view)
        inserter.start()
        queue.put({
            'type': 'redirect',
            'title': 'myArticle1',
            'target': 'myTarget1'
        })
        queue.put({
            'type': 'redirect',
            'title': 'myArticle2',
            'target': 'myTarget2'
        })
        queue.join()
        inserter.end()
        inserter.join()
        self.assertEqual(len(view.redirects), 2)
        self.assertEqual(view.redirects[0], ('myArticle1', 'myTarget1'))
        self.assertEqual(view.redirects[1], ('myArticle2', 'myTarget2'))
        self.assertEqual(view.commited, 2)
        self.assertEqual(view.cache_reset, 2)
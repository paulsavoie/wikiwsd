import unittest
import Queue
from wsd.build import NGramInserter
from wsd.tests.database.databasemocks import *

class NGramInserterTest(unittest.TestCase):

    def test_article(self):
        queue = Queue.Queue()
        view = BuildViewMock()
        inserter = NGramInserter(queue, view)
        inserter.start()
        queue.put({
            'type': 'article',
            'id': 1,
            'title': 'myArticle1',
            'text': 'This is [[target|an article]].'
        })
        queue.join()
        inserter.end()
        inserter.join()
        self.assertEqual(len(view.ngrams), 9)
        self.assertEqual(view.ngrams[0], ('This', 0))
        self.assertEqual(view.ngrams[1], ('is', 0))
        self.assertEqual(view.ngrams[2], ('an', 0))
        self.assertEqual(view.ngrams[3], ('article', 0))
        self.assertEqual(view.ngrams[4], ('This is', 0))
        self.assertEqual(view.ngrams[5], ('is an', 0))
        self.assertEqual(view.ngrams[6], ('an article', 1))
        self.assertEqual(view.ngrams[7], ('This is an', 0))
        self.assertEqual(view.ngrams[8], ('is an article', 0))
        self.assertEqual(view.commited, 1)
        self.assertEqual(view.cache_reset, 1)
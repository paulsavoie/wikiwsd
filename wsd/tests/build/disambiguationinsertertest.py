import unittest
import Queue
from wsd.build import DisambiguationInserter
from wsd.tests.database.databasemocks import *

class DisambiguationInserterTest(unittest.TestCase):

    def test_article(self):
        queue = Queue.Queue()
        view = BuildViewMock()
        inserter = DisambiguationInserter(queue, view)
        inserter.start()
        queue.put({
            'type': 'article',
            'id': 1,
            'title': 'myArticle1',
            'text': 'This is an [[article]] with another [[target|link]].'
        })
        queue.join()
        inserter.end()
        inserter.join()
        self.assertEqual(len(view.links), 2)
        self.assertEqual(len(view.disambiguations), 2)
        self.assertEqual(view.links[0], (1, 'article'))
        self.assertEqual(view.links[1], (1, 'target'))
        self.assertEqual(view.disambiguations[0], ('article', 'article'))
        self.assertEqual(view.disambiguations[1], ('link', 'target'))
        self.assertEqual(view.commited, 2)
        self.assertEqual(view.cache_reset, 1)
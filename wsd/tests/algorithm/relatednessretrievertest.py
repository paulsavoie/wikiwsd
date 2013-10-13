import unittest
from wsd.algorithm.relatednessretriever import RelatednessRetriever
from wsd.tests.database.databasemocks import *

class RelatednessRetrieverTest(unittest.TestCase):
    def setUp(self):
        self._work_view = WorkViewMock()
        self._retriever = RelatednessRetriever(self._work_view)

    def _retrieve_relatedness(self, id1, id2):
        link1 = {
            'target_article_id': id1,
            'target_article_name': 'Dummy Article 1'
        }
        link2 = {
            'target_article_id': id2,
            'target_article_name': 'Dummy Article 1'
        }
        return self._retriever.retrieve_relatedness(link1, link2)


    def test_simple(self):
        self._work_view.commons.append({
            'id1': 1, 'id2': 2, 'num': 3
        })
        result = self._retrieve_relatedness(1, 2)
        self.assertEqual(result, 3)
        self.assertEqual(self._work_view.query_counter, 1)

    def test_cache(self):
        self._work_view.commons.append({
            'id1': 1, 'id2': 2, 'num': 3
        })
        result = self._retrieve_relatedness(1, 2)
        result = self._retrieve_relatedness(2, 1)
        self.assertEqual(result, 3)
        self.assertEqual(self._work_view.query_counter, 1)

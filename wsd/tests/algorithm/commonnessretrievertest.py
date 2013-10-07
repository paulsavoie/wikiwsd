import unittest
from wsd.algorithm import CommonnessRetriever
from wsd.tests.database.databasemocks import *

class CommonnessRetrieverTest(unittest.TestCase):
    def setUp(self):
        self._work_view = WorkViewMock()
        self._retriever = CommonnessRetriever(self._work_view)

    def _retrieve_commonness(self, id1, id2):
        article1 = {
            'id': id1,
            'title': 'Dummy Article 1',
            'text': '',
            'links': []
        }
        article2 = {
            'id': id2,
            'title': 'Dummy Article 1',
            'text': '',
            'links': []
        }
        return self._retriever.retrieve_commonness(article1, article2)


    def test_simple(self):
        self._work_view.commons.append({
            'id1': 1, 'id2': 2, 'num': 3
        })
        result = self._retrieve_commonness(1, 2)
        self.assertEqual(result, 3)
        self.assertEqual(self._work_view.query_counter, 1)

    def test_cache(self):
        self._work_view.commons.append({
            'id1': 1, 'id2': 2, 'num': 3
        })
        result = self._retrieve_commonness(1, 2)
        result = self._retrieve_commonness(2, 1)
        self.assertEqual(result, 3)
        self.assertEqual(self._work_view.query_counter, 1)

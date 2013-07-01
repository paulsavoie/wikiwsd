import unittest
from wsd.commonnessretriever import CommonnessRetriever 

class CommonnessRetrieverTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_simple(self):
        connector = MockDBConnector()
        connector.commons = [
            { 'id1': 1, 'id2': 2, 'num': 3 }
        ]

        retriever = CommonnessRetriever(connector)
        result = retriever.retrieve_commonness({ 'id': 1 }, { 'id': 2})

        self.assertEqual(connector.called, 1)
        self.assertEqual(result, 3)

    def test_cache(self):
        connector = MockDBConnector()
        connector.commons = [
            { 'id1': 1, 'id2': 2, 'num': 3 }
        ]

        retriever = CommonnessRetriever(connector)
        result = retriever.retrieve_commonness({ 'id': 1 }, { 'id': 2})
        result = retriever.retrieve_commonness({ 'id': 2 }, { 'id': 1})

        self.assertEqual(connector.called, 1)
        self.assertEqual(result, 3)

class MockDBConnector():
    def __init__(self):
        self.commons = []
        self.called = 0

    def retrieve_number_of_common_articles(self, id1, id2):
        self.called += 1
        for common in self.commons:
            if (id1 == common['id1'] and id2 == common['id2']) or (id1 == common['id2'] and id2 == common['id1']):
                return common['num']
        return 0
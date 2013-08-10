import unittest
from wsd import MeaningFinder

class MeaningFinderTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_single_meaning(self):
        connector = MockDBConnector()
        connector.meanings = {
            'myNoun': [{
                'occurrences': 1,
                'name': 'meaning1',
                'id': 1,
                'articleincount': 2
            }]
        }
        terms = [
            { 'token': 'myNoun', 'isNoun': True, 'disambiguations': [] }
        ]
        finder = MeaningFinder(connector)
        finder.find_meanings(terms)

        self.assertEqual(connector.retrieve_meanings_called, 1)
        self.assertEqual(len(terms[0]['disambiguations']), 1)
        self.assertEqual(terms[0]['disambiguations'][0]['id'], 1)
        self.assertEqual(terms[0]['disambiguations'][0]['meaning'], 'meaning1')
        self.assertEqual(terms[0]['disambiguations'][0]['articleincount'], 2)
        self.assertEqual(terms[0]['disambiguations'][0]['percentage'], 1.0)

    def test_no_noun(self):
        connector = MockDBConnector()
        connector.meanings = {
            'myNoun': [{
                'occurrences': 1,
                'name': 'meaning1',
                'id': 1,
                'articleincount': 2
            }]
        }
        terms = [
            { 'token': 'noNoun', 'isNoun': False, 'disambiguations': [] },
            { 'token': 'myNoun', 'isNoun': True, 'disambiguations': [] }
        ]
        finder = MeaningFinder(connector)
        finder.find_meanings(terms)

        self.assertEqual(connector.retrieve_meanings_called, 1)
        self.assertEqual(len(terms[0]['disambiguations']), 0)
        self.assertEqual(len(terms[1]['disambiguations']), 1)

    def test_multiple_meanings(self):
        connector = MockDBConnector()
        connector.meanings = {
            'myNoun': [{
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
        }
        terms = [
            { 'token': 'myNoun', 'isNoun': True, 'disambiguations': [] }
        ]
        finder = MeaningFinder(connector)
        finder.find_meanings(terms)

        self.assertEqual(connector.retrieve_meanings_called, 1)
        self.assertEqual(len(terms[0]['disambiguations']), 2)
        self.assertEqual(terms[0]['disambiguations'][0]['id'], 1)
        self.assertEqual(terms[0]['disambiguations'][0]['meaning'], 'meaning1')
        self.assertEqual(terms[0]['disambiguations'][0]['articleincount'], 2)
        self.assertEqual(terms[0]['disambiguations'][0]['percentage'], 0.25)
        self.assertEqual(terms[0]['disambiguations'][1]['id'], 2)
        self.assertEqual(terms[0]['disambiguations'][1]['meaning'], 'meaning2')
        self.assertEqual(terms[0]['disambiguations'][1]['articleincount'], 3)
        self.assertEqual(terms[0]['disambiguations'][1]['percentage'], 0.75)

    def test_multiple_terms(self):
        connector = MockDBConnector()
        connector.meanings = {
            'myNoun': [{
                'occurrences': 1,
                'name': 'meaning1',
                'id': 1,
                'articleincount': 2
            }]
        }
        terms = [
            { 'token': 'myNoun', 'isNoun': True, 'disambiguations': [] },
            { 'token': 'myNoun2', 'isNoun': True, 'disambiguations': [] }
        ]
        finder = MeaningFinder(connector)
        finder.find_meanings(terms)

        self.assertEqual(connector.retrieve_meanings_called, 2)
        self.assertEqual(len(terms[0]['disambiguations']), 1)
        self.assertEqual(len(terms[1]['disambiguations']), 0)

    def test_same_term(self):
        connector = MockDBConnector()
        connector.meanings = {
            'myNoun': [{
                'occurrences': 1,
                'name': 'meaning1',
                'id': 1,
                'articleincount': 2
            }]
        }
        terms = [
            { 'token': 'myNoun', 'isNoun': True, 'disambiguations': [] },
            { 'token': 'myNoun', 'isNoun': True, 'disambiguations': [] }
        ]
        finder = MeaningFinder(connector)
        finder.find_meanings(terms)

        self.assertEqual(connector.retrieve_meanings_called, 1)
        self.assertEqual(len(terms[0]['disambiguations']), 1)
        self.assertEqual(len(terms[1]['disambiguations']), 1)

class MockDBConnector():
    def __init__(self):
        self.meanings = {}
        self.articles = {}
        self.retrieve_meanings_called = 0
        self.get_article_by_title_called = 0

    def retrieve_meanings(self, token):
        self.retrieve_meanings_called += 1
        if token in self.meanings:
            return self.meanings[token]
        return []

    def get_article_by_title(self, title):
        self.get_article_by_title_called += 1
        if title in self.articles:
            return self.articles[title]
        return None
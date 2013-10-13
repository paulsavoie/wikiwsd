import unittest
from wsd.runner.termidentifier import TermIdentifier

class TermIdentifierTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_simple_noun(self):
        identifier = TermIdentifier()
        article = identifier.identify_terms(u'I like houses.')
        self.assertEqual(len(article['links']), 1)
        self.assertEqual(article['text'], 'I like [[houses]] . ')
        self.assertEqual(article['links'][0]['phrase'], 'houses')

    def test_adjacent_noun(self):
        identifier = TermIdentifier()
        article = identifier.identify_terms(u'I like sugar cream.')
        self.assertEqual(len(article['links']), 1)
        self.assertEqual(article['text'], 'I like [[sugar cream]] . ')
        self.assertEqual(article['links'][0]['phrase'], 'sugar cream')

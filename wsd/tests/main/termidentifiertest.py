import unittest
from wsd.termidentifier import TermIdentifier

class TermIdentifierTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_simple_noun(self):
        identifier = TermIdentifier(None)
        terms = identifier.identify_terms(u'I like houses.')
        self.assertEqual(len(terms), 4)
        self.assertEqual(terms[0]['token'], u'I')
        self.assertEqual(terms[0]['index'], 0)
        self.assertEqual(terms[0]['length'], 1)
        self.assertEqual(terms[0]['isNoun'], False)
        self.assertEqual(terms[1]['token'], u'like')
        self.assertEqual(terms[1]['index'], 1)
        self.assertEqual(terms[1]['length'], 1)
        self.assertEqual(terms[1]['isNoun'], False)
        self.assertEqual(terms[2]['token'], u'houses')
        self.assertEqual(terms[2]['index'], 2)
        self.assertEqual(terms[2]['length'], 1)
        self.assertEqual(terms[2]['isNoun'], True)
        self.assertEqual(terms[3]['token'], u'.')
        self.assertEqual(terms[3]['index'], 3)
        self.assertEqual(terms[3]['length'], 1)
        self.assertEqual(terms[3]['isNoun'], False)

    def test_adjacent_noun(self):
        identifier = TermIdentifier(None)
        terms = identifier.identify_terms(u'I like sugar cream.')
        self.assertEqual(len(terms), 4)
        self.assertEqual(terms[0]['token'], u'I')
        self.assertEqual(terms[0]['index'], 0)
        self.assertEqual(terms[0]['length'], 1)
        self.assertEqual(terms[0]['isNoun'], False)
        self.assertEqual(terms[1]['token'], u'like')
        self.assertEqual(terms[1]['index'], 1)
        self.assertEqual(terms[1]['length'], 1)
        self.assertEqual(terms[1]['isNoun'], False)
        self.assertEqual(terms[2]['token'], u'sugar cream')
        self.assertEqual(terms[2]['index'], 2)
        self.assertEqual(terms[2]['length'], 2)
        self.assertEqual(terms[2]['isNoun'], True)
        self.assertEqual(terms[3]['token'], u'.')
        self.assertEqual(terms[3]['index'], 4)
        self.assertEqual(terms[3]['length'], 1)
        self.assertEqual(terms[3]['isNoun'], False)

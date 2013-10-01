import unittest
from wsd.evaluation.wikitermidentifier import WikiTermIdentifier

class WikiTermIdentifierTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse_text_only(self):
        identifier = WikiTermIdentifier()
        text = u'Just a text.\n'
        result = identifier.identify_terms(text)
        expected = {
            'terms': [
                { 'index': 1, 'token': u'Just', 'length': 1, 'isNoun': False },
                { 'index': 2, 'token': u'a', 'length': 1, 'isNoun': False },
                { 'index': 3, 'token': u'text.', 'length': 1, 'isNoun': False }
            ],
            'links': {}
        }
        self.assertEqual(result, expected)

    def test_remove_hyphens(self):
        identifier = WikiTermIdentifier()
        text = u'Just a text where someone says \'\'something\'\'\'.\n'
        result = identifier.identify_terms(text)
        expected = {
            'terms': [
                { 'index': 1, 'token': u'Just', 'length': 1, 'isNoun': False },
                { 'index': 2, 'token': u'a', 'length': 1, 'isNoun': False },
                { 'index': 3, 'token': u'text', 'length': 1, 'isNoun': False },
                { 'index': 4, 'token': u'where', 'length': 1, 'isNoun': False },
                { 'index': 5, 'token': u'someone', 'length': 1, 'isNoun': False },
                { 'index': 6, 'token': u'says', 'length': 1, 'isNoun': False },
                { 'index': 7, 'token': u'something.', 'length': 1, 'isNoun': False }
            ],
            'links': {}
        }
        self.assertEqual(result, expected)

    def test_single_line_comment(self):
        identifier = WikiTermIdentifier()
        text = u'Just a text.<!-- with a comment -->\n<!-- and another comment -->and more text\n'
        result = identifier.identify_terms(text)
        expected = {
            'terms': [
                { 'index': 1, 'token': u'Just', 'length': 1, 'isNoun': False },
                { 'index': 2, 'token': u'a', 'length': 1, 'isNoun': False },
                { 'index': 3, 'token': u'text.', 'length': 1, 'isNoun': False },
                { 'index': 4, 'token': u'and', 'length': 1, 'isNoun': False },
                { 'index': 5, 'token': u'more', 'length': 1, 'isNoun': False },
                { 'index': 6, 'token': u'text', 'length': 1, 'isNoun': False }
            ],
            'links': {}
        }
        self.assertEqual(result, expected)

    def test_multiple_line_comment(self):
        identifier = WikiTermIdentifier()
        text = u'Just a text.<!-- with a comment\nthat goes over a line\n and another line -->\n<!-- and another comment -->and more text\n'
        result = identifier.identify_terms(text)
        expected = {
            'terms': [
                { 'index': 1, 'token': u'Just', 'length': 1, 'isNoun': False },
                { 'index': 2, 'token': u'a', 'length': 1, 'isNoun': False },
                { 'index': 3, 'token': u'text.', 'length': 1, 'isNoun': False },
                { 'index': 4, 'token': u'and', 'length': 1, 'isNoun': False },
                { 'index': 5, 'token': u'more', 'length': 1, 'isNoun': False },
                { 'index': 6, 'token': u'text', 'length': 1, 'isNoun': False }
            ],
            'links': {}
        }
        self.assertEqual(result, expected)

    def test_inproper_lines(self):
        identifier = WikiTermIdentifier()
        text = u' | a wrong line\nJust a text.\n| and another wrong line\n! and another one\nand some proper text\n'
        result = identifier.identify_terms(text)
        expected = {
            'terms': [
                { 'index': 1, 'token': u'Just', 'length': 1, 'isNoun': False },
                { 'index': 2, 'token': u'a', 'length': 1, 'isNoun': False },
                { 'index': 3, 'token': u'text.', 'length': 1, 'isNoun': False },
                { 'index': 4, 'token': u'and', 'length': 1, 'isNoun': False },
                { 'index': 5, 'token': u'some', 'length': 1, 'isNoun': False },
                { 'index': 6, 'token': u'proper', 'length': 1, 'isNoun': False },
                { 'index': 7, 'token': u'text', 'length': 1, 'isNoun': False }
            ],
            'links': {}
        }
        self.assertEqual(result, expected)

    def test_incorrect_links(self):
        identifier = WikiTermIdentifier()
        text = u'Just a text with an incorrect [[cat:abc|cat]].\n'
        result = identifier.identify_terms(text)
        expected = {
            'terms': [
                { 'index': 1, 'token': u'Just', 'length': 1, 'isNoun': False },
                { 'index': 2, 'token': u'a', 'length': 1, 'isNoun': False },
                { 'index': 3, 'token': u'text', 'length': 1, 'isNoun': False },
                { 'index': 4, 'token': u'with', 'length': 1, 'isNoun': False },
                { 'index': 5, 'token': u'an', 'length': 1, 'isNoun': False },
                { 'index': 6, 'token': u'incorrect', 'length': 1, 'isNoun': False }
            ],
            'links': {}
        }
        self.assertEqual(result, expected)

    def test_link_in_links(self):
        identifier = WikiTermIdentifier()
        text = u'Just a text with a weird [[outer|cat[[inner:incorrect]] link]].\nAnd another [[cat:else|interesting [[combination]]]]\n'
        result = identifier.identify_terms(text)
        expected = {
            'terms': [
                { 'index': 1, 'token': u'Just', 'length': 1, 'isNoun': False },
                { 'index': 2, 'token': u'a', 'length': 1, 'isNoun': False },
                { 'index': 3, 'token': u'text', 'length': 1, 'isNoun': False },
                { 'index': 4, 'token': u'with', 'length': 1, 'isNoun': False },
                { 'index': 5, 'token': u'a', 'length': 1, 'isNoun': False },
                { 'index': 6, 'token': u'weird', 'length': 1, 'isNoun': False },
                { 'index': 9, 'token': u'And', 'length': 1, 'isNoun': False },
                { 'index': 10, 'token': u'another', 'length': 1, 'isNoun': False }
            ],
            'links': {}
        }
        self.assertEqual(result, expected)

    def test_blocks(self):
        identifier = WikiTermIdentifier()
        text = u'Just a text.\n{ and a block\n{ with another line\nand content again\n'
        result = identifier.identify_terms(text)
        expected = {
            'terms': [
                { 'index': 1, 'token': u'Just', 'length': 1, 'isNoun': False },
                { 'index': 2, 'token': u'a', 'length': 1, 'isNoun': False },
                { 'index': 3, 'token': u'text.', 'length': 1, 'isNoun': False },
                { 'index': 4, 'token': u'and', 'length': 1, 'isNoun': False },
                { 'index': 5, 'token': u'content', 'length': 1, 'isNoun': False },
                { 'index': 6, 'token': u'again', 'length': 1, 'isNoun': False }
            ],
            'links': {}
        }
        self.assertEqual(result, expected)

    def test_remove_empty_brackets(self):
        identifier = WikiTermIdentifier()
        text = u'Just a text with an incorrect ([[cat:abc|cat]]).\n'
        result = identifier.identify_terms(text)
        expected = {
            'terms': [
                { 'index': 1, 'token': u'Just', 'length': 1, 'isNoun': False },
                { 'index': 2, 'token': u'a', 'length': 1, 'isNoun': False },
                { 'index': 3, 'token': u'text', 'length': 1, 'isNoun': False },
                { 'index': 4, 'token': u'with', 'length': 1, 'isNoun': False },
                { 'index': 5, 'token': u'an', 'length': 1, 'isNoun': False },
                { 'index': 6, 'token': u'incorrect', 'length': 1, 'isNoun': False }
            ],
            'links': {}
        }
        self.assertEqual(result, expected)

    def test_take_care_of_whitespaces(self):
        identifier = WikiTermIdentifier()
        text = u'Just  a&nbsp;text.\n'
        result = identifier.identify_terms(text)
        expected = {
            'terms': [
                { 'index': 1, 'token': u'Just', 'length': 1, 'isNoun': False },
                { 'index': 2, 'token': u'a', 'length': 1, 'isNoun': False },
                { 'index': 3, 'token': u'text.', 'length': 1, 'isNoun': False }
            ],
            'links': {}
        }
        self.assertEqual(result, expected)

    def test_simple_link(self):
        identifier = WikiTermIdentifier()
        text = u'Just [[a text]].\n'
        result = identifier.identify_terms(text)
        expected = {
            'terms': [
                { 'index': 1, 'token': u'Just', 'length': 1, 'isNoun': False },
                { 'index': 2, 'token': u'a text', 'length': 2, 'isNoun': True,
                     'disambiguations': [], 'original': u'a text' }
            ],
            'links': { u'a text': 1 }
        }
        self.assertEqual(result, expected)

    def test_different_target_link(self):
        identifier = WikiTermIdentifier()
        text = u'Just [[target|a text]].\n'
        result = identifier.identify_terms(text)
        expected = {
            'terms': [
                { 'index': 1, 'token': u'Just', 'length': 1, 'isNoun': False },
                { 'index': 2, 'token': u'a text', 'length': 2, 'isNoun': True,
                     'disambiguations': [], 'original': u'target' }
            ],
            'links': { u'target': 1 }
        }
        self.assertEqual(result, expected)

    def test_multiple_links(self):
        identifier = WikiTermIdentifier()
        text = u'A longer [[text]] with many [[links]] that occur again here: [[links]]'
        result = identifier.identify_terms(text)
        expected = {
            u'text': 1,
            u'links': 2
        }
        self.assertEqual(result['links'], expected)

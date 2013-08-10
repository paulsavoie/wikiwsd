import unittest
import os
from wsd import HTMLOutputter 

class HTMLOutputterTest(unittest.TestCase):
    def setUp(self):
        self._test_dir = os.path.dirname(os.path.abspath(__file__))
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'main')
        header_path = os.path.join(root, 'header.html')
        footer_path = os.path.join(root, 'footer.html')
        with open(header_path, 'r') as header_f:
            self._header_html = header_f.read()
        with open(footer_path, 'r') as footer_f:
            self._footer_html = footer_f.read()
        self._term_header = ' <span class="noun">'
        self._disambiguation_header = '<div class="disambiguations"><ul><li class="header"><span class="label">Meaning</span><span class="percentage">Overall</span><span class="percentage">Rel.</span><span class="percentage">Comm.</span></li>'
        self._disambiguation_footer = '</ul></div>'
        self._term_footer = '</span>'

    def test_empty_text(self):
        outputter = HTMLOutputter()
        path = os.path.join(self._test_dir, 'test_empty_text.html')
        outputter.output([], path)

        expected = self._header_html
        expected += self._footer_html

        with open(path, 'r') as f:
            html = f.read()
            self.assertEqual(html, expected)

        os.remove(path)

    def test_single_entry_no_noun(self):
        outputter = HTMLOutputter()
        path = os.path.join(self._test_dir, 'test_single_entry_no_noun.html')
        outputter.output([{'token': 'myToken'}], path)

        expected = self._header_html
        #expected += self._term_header
        expected += ' myToken'
        #expected += self._term_footer
        expected += self._footer_html

        with open(path, 'r') as f:
            html = f.read()
            self.assertEqual(html[len(self._header_html):], expected[len(self._header_html):])

        os.remove(path)

    def test_single_entry_no_disambiguations(self):
        outputter = HTMLOutputter()
        path = os.path.join(self._test_dir, 'test_single_entry_no_disambiguations.html')
        outputter.output([{'token': 'myNoun', 'finalIndex': -1, 'disambiguations': []}], path)

        expected = self._header_html
        expected += self._term_header
        expected += 'myNoun'
        expected += self._disambiguation_header
        expected += self._disambiguation_footer
        expected += self._term_footer
        expected += self._footer_html

        with open(path, 'r') as f:
            html = f.read()
            self.assertEqual(html[len(self._header_html):], expected[len(self._header_html):])

        os.remove(path)

    def test_single_entry_single_disambiguation(self):
        outputter = HTMLOutputter()
        path = os.path.join(self._test_dir, 'test_single_entry.html')
        outputter.output([{'token': 'myNoun', 'finalIndex': 0, 'disambiguations': [
                { 'meaning': 'meaning1', 'overallMatch': 1.0, 'averageRelatedness': 0.5, 'percentage': 0.95, 'id': '1234' }
            ]}], path)

        expected = self._header_html
        expected += self._term_header
        expected += 'myNoun'
        expected += self._disambiguation_header
        expected += '<li class="selected"><span class="label">meaning1</span><span class="id">1234</span><span class="percentage">100%</span><span class="percentage">50%</span><span class="percentage">95%</span></li>'
        expected += self._disambiguation_footer
        expected += self._term_footer
        expected += self._footer_html

        with open(path, 'r') as f:
            html = f.read()
            self.assertEqual(html[len(self._header_html):], expected[len(self._header_html):])

        os.remove(path)

    def test_single_entry_multiple_disambiguation(self):
        outputter = HTMLOutputter()
        path = os.path.join(self._test_dir, 'test_single_entry_multiple_disambiguation.html')
        outputter.output([{'token': 'myNoun', 'finalIndex': 1, 'disambiguations': [
                { 'meaning': 'meaning1', 'overallMatch': 0.3, 'averageRelatedness': 0.5, 'percentage': 0.95, 'id': '1234' },
                { 'meaning': 'meaning2', 'overallMatch': 0.8, 'averageRelatedness': 0.4, 'percentage': 0.85, 'id': '5678' }
            ]}], path)

        expected = self._header_html
        expected += self._term_header
        expected += 'myNoun'
        expected += self._disambiguation_header
        expected += '<li class=""><span class="label">meaning1</span><span class="id">1234</span><span class="percentage">30%</span><span class="percentage">50%</span><span class="percentage">95%</span></li>'
        expected += '<li class="selected"><span class="label">meaning2</span><span class="id">5678</span><span class="percentage">80%</span><span class="percentage">40%</span><span class="percentage">85%</span></li>'
        expected += self._disambiguation_footer
        expected += self._term_footer
        expected += self._footer_html

        with open(path, 'r') as f:
            html = f.read()
            self.assertEqual(html[len(self._header_html):], expected[len(self._header_html):])

        os.remove(path)

    def test_multiple_entries(self):
        outputter = HTMLOutputter()
        path = os.path.join(self._test_dir, 'test_multiple_entries.html')
        outputter.output([{'token': 'myNoun', 'finalIndex': 0, 'disambiguations': [
                { 'meaning': 'meaning1', 'overallMatch': 1.0, 'averageRelatedness': 0.5, 'percentage': 0.95, 'id': '1234' }
            ]}, { 'token': 'myTerm' }], path)

        expected = self._header_html
        expected += self._term_header
        expected += 'myNoun'
        expected += self._disambiguation_header
        expected += '<li class="selected"><span class="label">meaning1</span><span class="id">1234</span><span class="percentage">100%</span><span class="percentage">50%</span><span class="percentage">95%</span></li>'
        expected += self._disambiguation_footer
        expected += self._term_footer
        expected += ' myTerm'
        expected += self._footer_html

        with open(path, 'r') as f:
            html = f.read()
            self.assertEqual(html[len(self._header_html):], expected[len(self._header_html):])

        os.remove(path)

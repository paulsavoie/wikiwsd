import unittest
import os
from wsd.runner.htmloutputter import HTMLOutputter 

class HTMLOutputterTest(unittest.TestCase):
    def setUp(self):
        self._test_dir = os.path.dirname(os.path.abspath(__file__))
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'runner')
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

    def _output_text(self, path, text, links=[]):
        article = {
            'id': None,
            'title': None,
            'text': text,
            'links': links
        }
        outputter = HTMLOutputter()
        outputter.output(article, path)
        return article

    def test_empty_text(self):
        path = os.path.join(self._test_dir, 'test_empty_text.html')
        article = self._output_text(path, '')

        expected = self._header_html
        expected += self._footer_html

        with open(path, 'r') as f:
            html = f.read()
            self.assertEqual(html, expected)

        os.remove(path)

    def test_single_entry_no_noun(self):
        path = os.path.join(self._test_dir, 'test_single_entry_no_noun.html')
        article = self._output_text(path, 'Single entry with no noun.')

        expected = self._header_html
        expected += 'Single entry with no noun.'
        expected += self._footer_html

        with open(path, 'r') as f:
            html = f.read()
            self.assertEqual(html[len(self._header_html):], expected[len(self._header_html):])

        os.remove(path)

    def test_single_entry_no_disambiguations(self):
        path = os.path.join(self._test_dir, 'test_single_entry_no_disambiguations.html')
        links = [
            { 'target_article_id': None, 'target_article_name': None, 'meanings': [] }
        ]
        article = self._output_text(path, 'Single entry with no [[disambiguation]].', links)

        expected = self._header_html
        expected += 'Single entry with no'
        expected += self._term_header
        expected += 'disambiguation. '
        expected += self._disambiguation_header
        expected += self._disambiguation_footer
        expected += self._term_footer
        expected += self._footer_html

        with open(path, 'r') as f:
            html = f.read()
            self.assertEqual(html[len(self._header_html):], expected[len(self._header_html):])

        os.remove(path)

    def test_single_entry_single_disambiguation(self):
        path = os.path.join(self._test_dir, 'test_single_entry.html')
        links = [
            { 'target_article_id': None, 'target_article_name': None, 'meanings': [
                { 'target_article_id': 1234, 'target_article_name': 'Dummy Meaning', 'phrase':'disambiguation', 'overallMatch': 1.0, 'relatedness': 0.5, 'commonness': 0.95 }
            ] }
        ]
        article = self._output_text(path, 'Single entry with single [[disambiguation]].', links)

        expected = self._header_html
        expected += 'Single entry with single'
        expected += self._term_header
        expected += 'disambiguation. '
        expected += self._disambiguation_header
        expected += '<li class="selected"><span class="label">Dummy Meaning</span><span class="id">1234</span><span class="percentage">100%</span><span class="percentage">50%</span><span class="percentage">95%</span></li>'
        expected += self._disambiguation_footer
        expected += self._term_footer
        expected += self._footer_html

        with open(path, 'r') as f:
            html = f.read()
            self.assertEqual(html[len(self._header_html):], expected[len(self._header_html):])

        os.remove(path)

    def test_single_entry_multiple_disambiguation(self):
        path = os.path.join(self._test_dir, 'test_single_entry_multiple_disambiguation.html')
        links = [
            { 'target_article_id': None, 'target_article_name': None, 'meanings': [
                { 'target_article_id': 1234, 'target_article_name': 'meaning1', 'phrase':'disambiguation', 'overallMatch': 0.3, 'relatedness': 0.5, 'commonness': 0.95 },
                { 'target_article_id': 5678, 'target_article_name': 'meaning2', 'phrase':'disambiguation', 'overallMatch': 0.8, 'relatedness': 0.4, 'commonness': 0.85 }
            ] }
        ]
        article = self._output_text(path, 'Single entry with multiple [[disambiguation]].', links)

        expected = self._header_html
        expected += 'Single entry with multiple'
        expected += self._term_header
        expected += 'disambiguation. '
        expected += self._disambiguation_header
        expected += '<li class="selected"><span class="label">meaning1</span><span class="id">1234</span><span class="percentage">30%</span><span class="percentage">50%</span><span class="percentage">95%</span></li>'
        expected += '<li><span class="label">meaning2</span><span class="id">5678</span><span class="percentage">80%</span><span class="percentage">40%</span><span class="percentage">85%</span></li>'
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
        links = [
            { 'target_article_id': None, 'target_article_name': None, 'meanings': [
                { 'target_article_id': 1234, 'target_article_name': 'meaning1', 'phrase':'disambiguation', 'overallMatch': 0.3, 'relatedness': 0.5, 'commonness': 0.95 }
            ] },
            { 'target_article_id': None, 'target_article_name': None, 'meanings': [
                { 'target_article_id': 5678, 'target_article_name': 'meaning2', 'phrase':'disambiguations', 'overallMatch': 0.8, 'relatedness': 0.4, 'commonness': 0.85 }
            ] }
        ]
        article = self._output_text(path, 'Single entry with multiple [[disambiguation]] and [[disambiguations]].', links)

        expected = self._header_html
        expected += 'Single entry with multiple'
        expected += self._term_header
        expected += 'disambiguation '
        expected += self._disambiguation_header
        expected += '<li class="selected"><span class="label">meaning1</span><span class="id">1234</span><span class="percentage">30%</span><span class="percentage">50%</span><span class="percentage">95%</span></li>'
        expected += self._disambiguation_footer
        expected += self._term_footer
        expected += 'and'
        expected += self._term_header
        expected += 'disambiguations. '
        expected += self._disambiguation_header
        expected += '<li class="selected"><span class="label">meaning2</span><span class="id">5678</span><span class="percentage">80%</span><span class="percentage">40%</span><span class="percentage">85%</span></li>'
        expected += self._disambiguation_footer
        expected += self._term_footer        
        expected += self._footer_html

        with open(path, 'r') as f:
            html = f.read()
            self.assertEqual(html[len(self._header_html):], expected[len(self._header_html):])

        os.remove(path)

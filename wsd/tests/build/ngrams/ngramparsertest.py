import unittest
from wsd.build.ngrams import NGramParser

class NGramParserTest(unittest.TestCase):
    def setUp(self):
        self._connection = MySQLMockConnection()

    def test_parse_text_only(self):
        parser = NGramParser(self._connection)
        text = u'Just a text.\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], text) # nothing should have changed

    def test_remove_hyphens(self):
        parser = NGramParser(self._connection)
        text = u'Just a text where someone says \'\'something\'\'\'.\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], u'Just a text where someone says something.\n')

    def test_single_line_comment(self):
        parser = NGramParser(self._connection)
        text = u'Just a text.<!-- with a comment -->\n<!-- and another comment -->and more text\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], u'Just a text.\nand more text\n')

    def test_multiple_line_comment(self):
        parser = NGramParser(self._connection)
        text = u'Just a text.<!-- with a comment\nthat goes over a line\n and another line -->\n<!-- and another comment -->and more text\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], u'Just a text.\nand more text\n')

    def test_html_tags_in_comment(self):
        parser = NGramParser(self._connection)
        text = u'Just a text.<!-- with a comment <div>with a <a href="here">tag</a>.</div> -->\n<!-- and another comment -->and more text\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], u'Just a text.\nand more text\n')

    def test_single_html_tag(self):
        parser = NGramParser(self._connection)
        text = u'Just a text<div class="abc">with a <a href="here>link</a> here</div>.\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], u'Just a text.\n')

    def test_html_tag_tree(self):
        parser = NGramParser(self._connection)
        text = u'Just a <div class="abc">with a <a href="here>link</a> here <br />which <p>spreads</p> over several <br /> lines</div>text.\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], u'Just a text.\n')

    def test_inproper_lines(self):
        parser = NGramParser(self._connection)
        text = u' | a wrong line\nJust a text.\n| and another wrong line\n! and another one\nand some proper text\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], u'Just a text.\nand some proper text\n')

    def test_incorrect_links(self):
        parser = NGramParser(self._connection)
        text = u'Just a text with an incorrect [[cat:abc|cat]].\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], u'Just a text with an incorrect .\n')

    def test_link_in_links(self):
        parser = NGramParser(self._connection)
        text = u'Just a text with a weird [[outer|cat[[inner:incorrect]] link]].\nAnd another [[cat:else|interesting [[combination]]]]\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], u'Just a text with a weird [[outer|cat link]].\nAnd another\n')

    def test_blocks(self):
        parser = NGramParser(self._connection)
        text = u'Just a text.\n{ and a block\n{ with another line\nand content again\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], u'Just a text.\nand content again\n')

    def test_remove_empty_brackets(self):
        parser = NGramParser(self._connection)
        text = u'Just a text with an incorrect ([[cat:abc|cat]]).\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], u'Just a text with an incorrect .\n')

    def test_take_care_of_whitespaces(self):
        parser = NGramParser(self._connection)
        text = u'Just  a&nbsp;text.\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], u'Just a text.\n')

    def test_strip_line(self):
        parser = NGramParser(self._connection)
        text = u'*** Just a text.\r\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], u'Just a text.\n')

    def test_remove_headers(self):
        parser = NGramParser(self._connection)
        text = u'===header1===\n====header 2====\nJust a text.\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], u'Just a text.\n')

    def test_remove_one_bracket_links(self):
        parser = NGramParser(self._connection)
        text = u'Just a text.[http://www.google.com]\n'
        article = { 'text': text }
        parser.parse_article(article)

        self.assertEqual(article['text'], u'Just a text.\n')

    def test_simple_ngrams(self):
        parser = NGramParser(self._connection)
        text = u'Just a text.\n'
        article = { 'text': text }
        parser.extract_n_grams(article)
        ngrams = self._stored_ngrams()
        self.assertTrue(('Just', '0') in ngrams)
        self.assertTrue(('a', '0') in ngrams)
        self.assertTrue(('text', '0') in ngrams)
        self.assertTrue(('Just a', '0') in ngrams)
        self.assertTrue(('a text', '0') in ngrams)
        self.assertTrue(('Just a text', '0') in ngrams)
        self.assertEqual(len(ngrams), 6)

    def test_ngrams_multiple_lines(self):
        parser = NGramParser(self._connection)
        text = u'a line\nanother\n'
        article = { 'text': text }
        parser.extract_n_grams(article)
        ngrams = self._stored_ngrams()
        self.assertTrue(('a', '0') in ngrams)
        self.assertTrue(('line', '0') in ngrams)
        self.assertTrue(('a line', '0') in ngrams)
        self.assertTrue(('another', '0') in ngrams)
        self.assertEqual(len(ngrams), 4)

    def test_simple_link(self):
        parser = NGramParser(self._connection)
        text = u'Just [[a text]].\n'
        article = { 'text': text }
        parser.extract_n_grams(article)
        ngrams = self._stored_ngrams()
        self.assertTrue(('Just', '0') in ngrams)
        self.assertTrue(('a', '0') in ngrams)
        self.assertTrue(('text', '0') in ngrams)
        self.assertTrue(('Just a', '0') in ngrams)
        self.assertTrue(('a text', '1') in ngrams)
        self.assertTrue(('Just a text', '0') in ngrams)
        self.assertEqual(len(ngrams), 6)

    def test_different_target_link(self):
        parser = NGramParser(self._connection)
        text = u'Just [[target|a text]].\n'
        article = { 'text': text }
        parser.extract_n_grams(article)
        ngrams = self._stored_ngrams()
        self.assertTrue(('Just', '0') in ngrams)
        self.assertTrue(('a', '0') in ngrams)
        self.assertTrue(('text', '0') in ngrams)
        self.assertTrue(('Just a', '0') in ngrams)
        self.assertTrue(('a text', '1') in ngrams)
        self.assertTrue(('Just a text', '0') in ngrams)
        self.assertEqual(len(ngrams), 6)

    def test_tokens(self):
        parser = NGramParser(self._connection)
        text = u'Just, a text.\n'
        article = { 'text': text }
        parser.extract_n_grams(article)
        ngrams = self._stored_ngrams()
        self.assertTrue(('Just', '0') in ngrams)
        self.assertTrue(('a', '0') in ngrams)
        self.assertTrue(('text', '0') in ngrams)
        self.assertTrue(('Just, a', '0') in ngrams)
        self.assertTrue(('a text', '0') in ngrams)
        self.assertTrue(('Just, a text', '0') in ngrams)
        self.assertEqual(len(ngrams), 6)

    def test_phrases(self):
        parser = NGramParser(self._connection)
        text = u'Just; a text.\n'
        article = { 'text': text }
        parser.extract_n_grams(article)
        ngrams = self._stored_ngrams()
        self.assertTrue(('Just', '0') in ngrams)
        self.assertTrue(('a', '0') in ngrams)
        self.assertTrue(('text', '0') in ngrams)
        self.assertTrue(('a text', '0') in ngrams)
        self.assertEqual(len(ngrams), 4)

    def test_whole_link(self):
        parser = NGramParser(self._connection)
        text = u'[[Just a text]]\n'
        article = { 'text': text }
        parser.extract_n_grams(article)
        ngrams = self._stored_ngrams()
        self.assertTrue(('Just', '0') in ngrams)
        self.assertTrue(('a', '0') in ngrams)
        self.assertTrue(('text', '0') in ngrams)
        self.assertTrue(('Just a', '0') in ngrams)
        self.assertTrue(('a text', '0') in ngrams)
        self.assertTrue(('Just a text', '1') in ngrams)
        self.assertEqual(len(ngrams), 6)

    def test_strip_ngrams(self):
        parser = NGramParser(self._connection)
        text = u'Just a text._ \n'
        article = { 'text': text }
        parser.extract_n_grams(article)
        ngrams = self._stored_ngrams()
        self.assertTrue(('Just', '0') in ngrams)
        self.assertTrue(('a', '0') in ngrams)
        self.assertTrue(('text', '0') in ngrams)
        self.assertTrue(('Just a', '0') in ngrams)
        self.assertTrue(('a text', '0') in ngrams)
        self.assertTrue(('Just a text', '0') in ngrams)
        self.assertEqual(len(ngrams), 6)

    def _stored_ngrams(self):
        ngrams = []
        for query in self._connection.cur.queries:
            if query[0:19] == 'INSERT INTO ngrams_':
                start_index = query.find('VALUES(')+7
                first_comma = query.find(', 1, ', start_index)
                second_comma = first_comma+3
                end_index = query.find(')', second_comma)
                ngram = query[start_index:first_comma]
                link = query[second_comma+2:end_index]
                ngrams.append((ngram, link))
            else:
                return []
        return ngrams

class MySQLMockCursor():
    def __init__(self):
        self.queries = []
        self.return_vals = {}

    def execute(self, *args):
        query = args[0]
        arguments = args[1]
        index = 0
        while (query.find('%s') != -1):
            query = query.replace('%s', str(arguments[index]), 1)
            index += 1
        self.queries.append(query)
        if (query in self.return_vals):
            return self.return_vals[query]
        return None

    def executemany(self, query, items):
        for item in items:
            self.execute(query, item)


class MySQLMockConnection():
    def __init__(self):
        self.cur = MySQLMockCursor()
        self.commit_called = 0

    def cursor(self):
        return self.cur

    def commit(self):
        self.commit_called += 1
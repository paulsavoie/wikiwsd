import unittest
import Queue
import xml.sax
from wsd.creator.wikiparser import WikiParser

class WikiParserTest(unittest.TestCase):
    def setUp(self):
        self._connection = MySQLMockConnection()

    def test_empty_article(self):
        parser = WikiParser(self._connection)
        parser.parse_article({ 'id': 1, 'title': 'myArticle', 'text': u''})

        self.assertEqual(len(self._connection.cur.queries), 0)

    def test_single_link(self):
        parser = WikiParser(self._connection)
        article = { 'id': 1, 'title': 'myArticle', 'text': u'This is a [[target_name|link]].'}

        self._connection.cur.return_vals['SELECT id, title, articleincount FROM articles WHERE title=target_name;'] = (2, 'myTarget', 1)

        parser.parse_article(article)

        self.assertEqual(len(self._connection.cur.queries), 4)
        self.assertEqual(self._connection.cur.queries[0], 'SELECT id, title, articleincount FROM articles WHERE title=target_name;')
        self.assertEqual(self._connection.cur.queries[1], 'INSERT INTO links(source_article_id, target_article_id, count) VALUES(1, 2, 1);')
        self.assertEqual(self._connection.cur.queries[2], 'UPDATE articles SET articleincount=articleincount+1 WHERE id=2;')
        self.assertEqual(self._connection.cur.queries[3], 'INSERT INTO disambiguations(string, target_article_id, occurrences) VALUES(link, 2, 1) ON DUPLICATE KEY UPDATE occurrences=occurrences+1;')

    def test_single_redirect(self):
        parser = WikiParser(self._connection)
        article = { 'id': 1, 'title': 'myArticle', 'text': u'This is a [[redirect_name|link]].'}
        self._connection.cur.return_vals['SELECT id, title, articleincount FROM articles WHERE title=target_name;'] = (2, 'myTarget', 1)
        self._connection.cur.return_vals['SELECT target_article_name FROM redirects WHERE source_article_name=redirect_name;'] = ['target_name']
        
        parser.parse_article(article)

        self.assertEqual(len(self._connection.cur.queries), 6)
        self.assertEqual(self._connection.cur.queries[0], 'SELECT id, title, articleincount FROM articles WHERE title=redirect_name;')
        self.assertEqual(self._connection.cur.queries[1], 'SELECT target_article_name FROM redirects WHERE source_article_name=redirect_name;')
        self.assertEqual(self._connection.cur.queries[2], 'SELECT id, title, articleincount FROM articles WHERE title=target_name;')
        self.assertEqual(self._connection.cur.queries[3], 'INSERT INTO links(source_article_id, target_article_id, count) VALUES(1, 2, 1);')
        self.assertEqual(self._connection.cur.queries[4], 'UPDATE articles SET articleincount=articleincount+1 WHERE id=2;')
        self.assertEqual(self._connection.cur.queries[5], 'INSERT INTO disambiguations(string, target_article_id, occurrences) VALUES(link, 2, 1) ON DUPLICATE KEY UPDATE occurrences=occurrences+1;')

    def test_anchor_link(self):
        parser = WikiParser(self._connection)
        article = { 'id': 1, 'title': 'myArticle', 'text': u'This is a [[target_name#anchor-name|link]].'}
        self._connection.cur.return_vals['SELECT id, title, articleincount FROM articles WHERE title=target_name;'] = (2, 'myTarget', 1)

        parser.parse_article(article)

        self.assertEqual(len(self._connection.cur.queries), 4)
        self.assertEqual(self._connection.cur.queries[0], 'SELECT id, title, articleincount FROM articles WHERE title=target_name;')
        self.assertEqual(self._connection.cur.queries[1], 'INSERT INTO links(source_article_id, target_article_id, count) VALUES(1, 2, 1);')
        self.assertEqual(self._connection.cur.queries[2], 'UPDATE articles SET articleincount=articleincount+1 WHERE id=2;')
        self.assertEqual(self._connection.cur.queries[3], 'INSERT INTO disambiguations(string, target_article_id, occurrences) VALUES(link, 2, 1) ON DUPLICATE KEY UPDATE occurrences=occurrences+1;')

    def test_language_link(self):
        parser = WikiParser(self._connection)
        parser.parse_article({ 'id': 1, 'title': 'myArticle', 'text': u'[[sk:Anarchizmus]]'})

        self.assertEqual(len(self._connection.cur.queries), 0)

    def test_spaces_in_link(self):
        parser = WikiParser(self._connection)
        article = { 'id': 1, 'title': 'myArticle', 'text': u'This is a [[link to an article]].'}
        self._connection.cur.return_vals['SELECT id, title, articleincount FROM articles WHERE title=link to an article;'] = (2, 'myTarget', 1)

        parser.parse_article(article)

        self.assertEqual(len(self._connection.cur.queries), 4)
        self.assertEqual(self._connection.cur.queries[0], 'SELECT id, title, articleincount FROM articles WHERE title=link to an article;')
        self.assertEqual(self._connection.cur.queries[1], 'INSERT INTO links(source_article_id, target_article_id, count) VALUES(1, 2, 1);')
        self.assertEqual(self._connection.cur.queries[2], 'UPDATE articles SET articleincount=articleincount+1 WHERE id=2;')
        self.assertEqual(self._connection.cur.queries[3], 'INSERT INTO disambiguations(string, target_article_id, occurrences) VALUES(link to an article, 2, 1) ON DUPLICATE KEY UPDATE occurrences=occurrences+1;')

    def test_spaces_in_target(self):
        parser = WikiParser(self._connection)
        article = { 'id': 1, 'title': 'myArticle', 'text': u'This is a [[another article|link]].'}
        self._connection.cur.return_vals['SELECT id, title, articleincount FROM articles WHERE title=another article;'] = (2, 'myTarget', 1)
        parser.parse_article(article)

        self.assertEqual(len(self._connection.cur.queries), 4)
        self.assertEqual(self._connection.cur.queries[0], 'SELECT id, title, articleincount FROM articles WHERE title=another article;')
        self.assertEqual(self._connection.cur.queries[1], 'INSERT INTO links(source_article_id, target_article_id, count) VALUES(1, 2, 1);')
        self.assertEqual(self._connection.cur.queries[2], 'UPDATE articles SET articleincount=articleincount+1 WHERE id=2;')
        self.assertEqual(self._connection.cur.queries[3], 'INSERT INTO disambiguations(string, target_article_id, occurrences) VALUES(link, 2, 1) ON DUPLICATE KEY UPDATE occurrences=occurrences+1;')

    def test_own_link(self):
        parser = WikiParser(self._connection)
        parser.parse_article({ 'id': 12345, 'title': 'myArticle', 'text': u'[[link]]'})

        self.assertEqual(len(self._connection.cur.queries), 2)
        self.assertEqual(self._connection.cur.queries[0], 'SELECT id, title, articleincount FROM articles WHERE title=link;')
        self.assertEqual(self._connection.cur.queries[1], 'SELECT target_article_name FROM redirects WHERE source_article_name=link;')


class MySQLMockCursor():
    def __init__(self):
        self.queries = []
        self.return_vals = {}
        self._last_query = None

    def execute(self, *args):
        query = args[0]
        arguments = args[1]
        if isinstance(arguments, basestring) or isinstance(arguments, int):
            arguments = [arguments]
        index = 0
        while (query.find('%s') != -1):
            query = query.replace('%s', str(arguments[index]), 1)
            index += 1
        self.queries.append(query)
        self._last_query = query
        return None

    def fetchone(self):
        if self._last_query in self.return_vals:
            return self.return_vals[self._last_query]
        return None


class MySQLMockConnection():
    def __init__(self):
        self.cur = MySQLMockCursor()
        self.commit_called = 0

    def cursor(self):
        return self.cur

    def commit(self):
        self.commit_called += 1


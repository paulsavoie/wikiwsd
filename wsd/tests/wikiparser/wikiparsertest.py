import unittest
import Queue
import xml.sax
from wsd.creator.wikiparser import WikiParser

class WikiParserTest(unittest.TestCase):
    def setUp(self):
        self._articles = MockMongoTable('articles')
        self._redirects = MockMongoTable('redirects')
        self._meanings = MockMongoTable('meanings')
        db = MockMongoDB(self._articles, self._redirects, self._meanings)
        self._client = MockMongoClient( databases={ 'myDB': db })

    def test_empty_article(self):
        parser = WikiParser(self._client, 'myDB')
        parser.parse_article({ 'id': 1, 'title': 'myArticle', 'text': u''})

        self.assertEqual(self._articles.update_called, 0, 'Articles were updated without a link')
        self.assertEqual(self._articles.find_one_called, 0, 'Articles were searched without a link')
        self.assertEqual(self._redirects.update_called, 0, 'Redirects were updated without a link')
        self.assertEqual(self._redirects.find_one_called, 0, 'Redirects were searched without a link')
        self.assertEqual(self._meanings.update_called, 0, 'Meanings were updated without a link')
        self.assertEqual(self._meanings.find_one_called, 0, 'Meanings were searched without a link')

    def test_single_link(self):
        parser = WikiParser(self._client, 'myDB')
        article = { 'id': 1, 'title': 'myArticle', 'text': u'This is a [[target_name|link]].'}
        parser.parse_article(article)

        meaning = { '$setOnInsert': { 'targets.12345': { 'id': 12345, 'title': 'target_name', 'count': 0 } } , 
                      '$inc': { 'targets.12345.count' : 1 } }

        self.assertEqual(self._articles.update_called, 1)
        self.assertEqual(self._articles.find_one_called, 1)
        self.assertEqual(self._redirects.update_called, 0)
        self.assertEqual(self._redirects.find_one_called, 0)
        self.assertEqual(self._meanings.update_called, 1)
        self.assertEqual(self._meanings.find_one_called, 0)
        self.assertEqual(len(self._meanings.updates), 1)
        self.assertEqual(self._meanings.updates[0][0], { 'string': 'link' }, 'Wrong selector for meanings update')
        self.assertEqual(self._meanings.updates[0][1], meaning, 'Wrong value for meanings update')
        self.assertEqual(self._meanings.updates[0][2], True, 'Upsert not set for meanings update')
        self.assertEqual(self._articles.updates[0][0], { 'title': 'target_name' }, 'Wrong selector for articles update')
        self.assertEqual(self._articles.updates[0][1], { '$push': { "articles_link_here" : { "article": 12345, 'incount': 1 } } }, 'Wrong value for articles update')
        self.assertEqual(self._articles.updates[0][2], False, 'Upsert not set for articles update')

    def test_single_redirect(self):
        parser = WikiParser(self._client, 'myDB')
        article = { 'id': 1, 'title': 'myArticle', 'text': u'This is a [[redirect_name|link]].'}
        redirect = { 'source': u'redirect_name', 'target': u'target_name' }
        self._redirects.redirects[u'redirect_name'] = redirect
        self._articles.redirects[u'redirect_name'] = None # article does not exist
        parser.parse_article(article)

        meaning = { '$setOnInsert': { 'targets.12345': { 'id': 12345, 'title': 'target_name', 'count': 0 } } , 
                      '$inc': { 'targets.12345.count' : 1 } }

        self.assertEqual(self._articles.update_called, 1)
        self.assertEqual(self._articles.find_one_called, 2)
        self.assertEqual(self._redirects.update_called, 0)
        self.assertEqual(self._redirects.find_one_called, 1)
        self.assertEqual(self._meanings.update_called, 1)
        self.assertEqual(self._meanings.find_one_called, 0)
        self.assertEqual(len(self._meanings.updates), 1)
        self.assertEqual(self._meanings.updates[0][0], { 'string': 'link' }, 'Wrong selector for meanings update')
        self.assertEqual(self._meanings.updates[0][1], meaning, 'Wrong value for meanings update')
        self.assertEqual(self._meanings.updates[0][2], True, 'Upsert not set for meanings update')
        self.assertEqual(self._articles.updates[0][0], { 'title': 'target_name' }, 'Wrong selector for articles update')
        self.assertEqual(self._articles.updates[0][1], { '$push': { "articles_link_here" : { "article": 12345, 'incount': 1 } } }, 'Wrong value for articles update')
        self.assertEqual(self._articles.updates[0][2], False, 'Upsert not set for articles update')

class MockMongoDB():
    def __init__(self, articles, redirects, meanings):
        self.articles = articles
        self.redirects = redirects
        self.meanings = meanings

class MockMongoClient():
    def __init__(self, databases={}):
        self._databases = databases

    def __getitem__(self, k):
        if k in self._databases:
            return self._databases[k]
        raise AttributeError

class MockMongoTable():
    def __init__(self, name):
        self.name = name
        self.updates = []
        self.redirects = {}
        self.update_called = 0
        self.find_one_called = 0

    def update(self, selector, update, upsert=False):
        self.update_called += 1
        self.updates.append((selector, update, upsert))

    def find_one(self, selector):
        self.find_one_called += 1
        if self.name == 'articles':
            if selector['title'] in self.redirects:
                return None
            else:
                return {
                    'id': 12345,
                    'title': selector['title']
                }
        elif self.name == 'redirects':
            return self.redirects[selector['source']]

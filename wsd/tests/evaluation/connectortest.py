import unittest
from wsd.evaluation.connector import EvaluationConnector

class EvaluationConnectorTest(unittest.TestCase):
    def setUp(self):
        self.mock = MockDBConnector()
        sample = {
            'title': 'my sample',
            'id': 1,
            'links': {'myLink1': 2, 'myLink2': 1}
        }
        self.connector = EvaluationConnector(self.mock, sample)

    def test_article_by_title_own_link(self):
        self.assertEqual(self.connector.get_article_by_title('my sample'), None)

    def test_article_by_title_non_existent(self):
        self.assertEqual(self.connector.get_article_by_title('non existent'), None)

    def test_article_by_title(self):
        article = {
            'title': 'new article',
            'articleincount': 3
        }
        self.mock._articles.append(article)
        self.assertEqual(self.connector.get_article_by_title('new article'), article)

    def test_article_by_title_link_decrease(self):
        article = {
            'title': 'myLink1',
            'articleincount': 3
        }
        changed = {
            'title': 'myLink1',
            'articleincount': 2
        }
        self.mock._articles.append(article)
        self.assertEqual(self.connector.get_article_by_title('myLink1'), changed)

    def test_article_by_id_own_link(self):
        self.assertEqual(self.connector.get_article_by_id(1), None)

    def test_article_by_id_not_existent(self):
        self.assertEqual(self.connector.get_article_by_id(1111), None)

    def test_article_by_id(self):
        article = {
            'id': 2,
            'title': 'new article',
            'articleincount': 3
        }
        self.mock._articles.append(article)
        self.assertEqual(self.connector.get_article_by_id(2), article)

    def test_article_by_id_link_decrease(self):
        article = {
            'id': 2,
            'title': 'myLink1',
            'articleincount': 3
        }
        changed = {
            'id': 2,
            'title': 'myLink1',
            'articleincount': 2
        }
        self.mock._articles.append(article)
        self.assertEqual(self.connector.get_article_by_id(2), changed)

    def test_resolve_redirect(self):
        self.mock._redirects['my redirect'] = 'my target'
        self.assertEqual(self.connector.resolve_redirect('my redirect'), 'my target')

    def test_number_of_common_articles(self):
        article1 = {
            'id': 2,
            'title': 'myArticle1',
            'articleincount': 3
        }
        article2 = {
            'id': 3,
            'title': 'myArticle2',
            'articleincount': 3
        }
        self.mock._articles.append(article1)
        self.mock._articles.append(article2)
        self.mock._common_articles.append({ 'ids': (2,3), 'value': 7})
        self.assertEqual(self.connector.retrieve_number_of_common_articles(2,3), 7)

    def test_number_of_common_articles_reduce_link(self):
        article1 = {
            'id': 2,
            'title': 'myLink1',
            'articleincount': 3
        }
        article2 = {
            'id': 3,
            'title': 'myLink2',
            'articleincount': 3
        }
        self.mock._articles.append(article1)
        self.mock._articles.append(article2)
        self.mock._common_articles.append({ 'ids': (2,3), 'value': 7})
        self.assertEqual(self.connector.retrieve_number_of_common_articles(2,3), 6)

    def test_number_of_common_articles_default_to_zero(self):
        article1 = {
            'id': 2,
            'title': 'myLink1',
            'articleincount': 3
        }
        article2 = {
            'id': 3,
            'title': 'myLink2',
            'articleincount': 3
        }
        self.mock._articles.append(article1)
        self.mock._articles.append(article2)
        self.mock._common_articles.append({ 'ids': (2,3), 'value': 0})
        self.assertEqual(self.connector.retrieve_number_of_common_articles(2,3), 0)

    def test_retrieve_meanings(self):
        meaning1 = {
            'name': 'meaning 1',
            'articleincount': 3,
            'occurrences': 5
        }
        meaning2 = {
            'name': 'meaning 2',
            'articleincount': 1,
            'occurrences': 2
        }
        meanings = [meaning1, meaning2]
        self.mock._meanings['term'] = meanings

        self.assertEqual(self.connector.retrieve_meanings('term'), meanings)

    def test_retrieve_meanings_reduce(self):
        meaning1 = {
            'name': 'myLink1',
            'articleincount': 3,
            'occurrences': 5
        }
        meaning2 = {
            'name': 'myLink2',
            'articleincount': 1,
            'occurrences': 2
        }
        meanings = [meaning1, meaning2]
        self.mock._meanings['term'] = meanings

        reduced = [{ 'name': 'myLink1', 'articleincount': 2, 'occurrences': 3}]

        self.assertEqual(self.connector.retrieve_meanings('term'), reduced)

class MockDBConnector:
    def __init__(self):
        self._articles = []
        self._redirects = {}
        self._common_articles = []
        self._meanings = {}

    def get_article_by_title(self, title):
        for article in self._articles:
            if article['title'] == title:
                return article
        return None

    def get_article_by_id(self, id):
        for article in self._articles:
            if article['id'] == id:
                return article
        return None

    def resolve_redirect(self, name):
        if name in self._redirects:
            return self._redirects[name]
        return None

    def retrieve_number_of_common_articles(self, id1, id2):
        for common in self._common_articles:
            if id1 in common['ids'] and id2 in common['ids']:
                return common['value']
        return None

    def retrieve_meanings(self, name):
        for meaning in self._meanings:
            if meaning == name:
                return self._meanings[meaning]
        return ()

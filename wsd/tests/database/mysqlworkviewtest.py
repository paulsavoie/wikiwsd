import unittest
from wsd.database import MySQLWorkView
from mysqlmocks import *

class MySQLWorkViewTest(unittest.TestCase):

    def test_destructor(self):
        conn = MockMySQLConnection()
        view = MySQLWorkView(conn)
        self.assertEqual(conn.closed, False)
        del view
        self.assertEqual(conn.closed, True)

    def test_resolve_redirect(self):
        conn = MockMySQLConnection()
        view = MySQLWorkView(conn)
        conn.cursor().return_vals['SELECT target_article_name FROM redirects WHERE source_article_name=myRedirect;'] = ['myTarget'];
        target = view.resolve_redirect('myRedirect')
        self.assertEqual(len(conn.cursor().queries), 1)
        self.assertEqual(conn.cursor().queries[0], 'SELECT target_article_name FROM redirects WHERE source_article_name=myRedirect;')
        self.assertEqual(target, 'myTarget')

    def test_resolve_redirect_fail(self):
        conn = MockMySQLConnection()
        view = MySQLWorkView(conn)
        target = view.resolve_redirect('myRedirect')
        self.assertEqual(len(conn.cursor().queries), 1)
        self.assertEqual(conn.cursor().queries[0], 'SELECT target_article_name FROM redirects WHERE source_article_name=myRedirect;')
        self.assertEqual(target, None)

    def test_retrieve_number_of_common_articles(self):
        conn = MockMySQLConnection()
        view = MySQLWorkView(conn)
        conn.cursor().return_vals['SELECT source_article_id FROM links WHERE target_article_id=100;'] = [1,2,4,8,16,32];
        conn.cursor().return_vals['SELECT source_article_id FROM links WHERE target_article_id=200;'] = [1,2,3,4,5,6,7];
        num = view.retrieve_number_of_common_articles(100, 200)
        self.assertEqual(len(conn.cursor().queries), 2)
        self.assertEqual(conn.cursor().queries[0], 'SELECT source_article_id FROM links WHERE target_article_id=100;')
        self.assertEqual(conn.cursor().queries[1], 'SELECT source_article_id FROM links WHERE target_article_id=200;')
        self.assertEqual(num, 3)

    def test_retrieve_number_of_common_articles_cache(self):
        conn = MockMySQLConnection()
        view = MySQLWorkView(conn)
        conn.cursor().return_vals['SELECT source_article_id FROM links WHERE target_article_id=100;'] = [1,2,4,8,16,32];
        conn.cursor().return_vals['SELECT source_article_id FROM links WHERE target_article_id=200;'] = [1,2,3,4,5,6,7];
        conn.cursor().return_vals['SELECT source_article_id FROM links WHERE target_article_id=300;'] = [1,2,3,4,5,6];
        view.retrieve_number_of_common_articles(100, 200)
        num = view.retrieve_number_of_common_articles(300, 200)
        self.assertEqual(len(conn.cursor().queries), 3)
        self.assertEqual(num, 6)

    def test_retrieve_meanings(self):
        conn = MockMySQLConnection()
        view = MySQLWorkView(conn)
        conn.cursor().return_vals['SELECT target_article_id, SUM(occurrences) AS occurrences FROM disambiguations WHERE string=myTerm GROUP BY target_article_id ORDER BY occurrences DESC;'] = [(1,7),(2,3),(3,1)]
        conn.cursor().return_vals['SELECT id, title, articleincount FROM articles WHERE id IN (1,2,3);'] = [(1, 'myMeaning1', 7), (3, 'myMeaning3', 100)]
        meanings = view.retrieve_meanings('myTerm')
        self.assertEqual(len(conn.cursor().queries), 2)
        self.assertEqual(conn.cursor().queries[0], 'SELECT target_article_id, SUM(occurrences) AS occurrences FROM disambiguations WHERE string=myTerm GROUP BY target_article_id ORDER BY occurrences DESC;')
        self.assertEqual(conn.cursor().queries[1], 'SELECT id, title, articleincount FROM articles WHERE id IN (1,2,3);')
        self.assertEqual(len(meanings), 2)
        self.assertEqual(meanings[0], { 'id': 1, 'title': 'myMeaning1', 'articleincount': 7, 'occurrences': 7 })
        self.assertEqual(meanings[1], { 'id': 3, 'title': 'myMeaning3', 'articleincount': 100, 'occurrences': 1 })

    def test_resolve_title(self):
        conn = MockMySQLConnection()
        view = MySQLWorkView(conn)
        conn.cursor().return_vals['SELECT id, title FROM articles WHERE title=myArticle;'] = [1, 'myArticle']
        article = view.resolve_title('myArticle')
        self.assertEqual(len(conn.cursor().queries), 1)
        self.assertEqual(conn.cursor().queries[0], 'SELECT id, title FROM articles WHERE title=myArticle;')
        self.assertEqual(article['id'], 1)
        self.assertEqual(article['title'], 'myArticle')

    def test_resolve_title_redirect(self):
        conn = MockMySQLConnection()
        view = MySQLWorkView(conn)
        conn.cursor().return_vals['SELECT id, title FROM articles WHERE title=(SELECT target_article_name FROM redirects WHERE source_article_name=myRedirect);'] = [1, 'myArticle']
        article = view.resolve_title('myRedirect')
        self.assertEqual(len(conn.cursor().queries), 2)
        self.assertEqual(conn.cursor().queries[0], 'SELECT id, title FROM articles WHERE title=myRedirect;')
        self.assertEqual(conn.cursor().queries[1], 'SELECT id, title FROM articles WHERE title=(SELECT target_article_name FROM redirects WHERE source_article_name=myRedirect);')
        self.assertEqual(article['id'], 1)
        self.assertEqual(article['title'], 'myArticle')

    def test_resolve_title_cache(self):
        conn = MockMySQLConnection()
        view = MySQLWorkView(conn)
        conn.cursor().return_vals['SELECT id, title FROM articles WHERE title=(SELECT target_article_name FROM redirects WHERE source_article_name=myRedirect);'] = [1, 'myArticle']
        view.resolve_title('myRedirect')

        article1 = view.resolve_title('myArticle')
        article2 = view.resolve_title('myRedirect')
        self.assertEqual(len(conn.cursor().queries), 2)
        self.assertEqual(article1['id'], 1)
        self.assertEqual(article1['title'], 'myArticle')
        self.assertEqual(article1, article2)
    
    def test_retrieve_occurences(self):
        conn = MockMySQLConnection()
        view = MySQLWorkView(conn)
        conn.cursor().return_vals['SELECT occurrences, as_link FROM ngrams_m WHERE string=myPhrase;'] = [7, 2]
        result = view.retrieve_occurences('myPhrase')

        self.assertEqual(len(conn.cursor().queries), 1)
        self.assertEqual(result['occurrences'], 7)
        self.assertEqual(result['as_link'], 2)

    def test_retrieve_occurences_cache(self):
        conn = MockMySQLConnection()
        view = MySQLWorkView(conn)
        conn.cursor().return_vals['SELECT occurrences, as_link FROM ngrams_m WHERE string=myPhrase;'] = [7, 2]
        result = view.retrieve_occurences('myPhrase')
        result = view.retrieve_occurences('myPhrase')

        self.assertEqual(len(conn.cursor().queries), 1)
        self.assertEqual(result['occurrences'], 7)
        self.assertEqual(result['as_link'], 2)
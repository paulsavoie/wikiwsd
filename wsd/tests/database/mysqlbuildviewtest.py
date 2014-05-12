import unittest
from wsd.database import MySQLBuildView
from mysqlmocks import *

class MySQLBuildViewTest(unittest.TestCase):

    def test_destructor(self):
        conn = MockMySQLConnection()
        view = MySQLBuildView(conn)
        self.assertEqual(conn.closed, False)
        del view
        self.assertEqual(conn.closed, True)

    def test_insert_article(self):
        conn = MockMySQLConnection()
        view = MySQLBuildView(conn)
        view.insert_article(1, 'myTitle')
        self.assertEqual(len(conn.cursor().queries), 1)
        self.assertEqual(conn.cursor().queries[0], 'INSERT INTO articles(id, title) VALUES(1, myTitle);')

    def test_insert_redirect(self):
        conn = MockMySQLConnection()
        view = MySQLBuildView(conn)
        view.insert_redirect('mySource', 'myTarget')
        self.assertEqual(len(conn.cursor().queries), 1)
        self.assertEqual(conn.cursor().queries[0], 
            'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mySource, myTarget);')

    def test_insert_link(self):
        conn = MockMySQLConnection()
        view = MySQLBuildView(conn)
        conn.cursor().return_vals['SELECT id FROM articles WHERE title=myTarget;'] = [2];
        view.insert_link(1, 'myTarget')
        self.assertEqual(len(conn.cursor().queries), 2)
        self.assertEqual(conn.cursor().queries[0], 
            'SELECT id FROM articles WHERE title=myTarget;')
        self.assertEqual(conn.cursor().queries[1],
            'INSERT INTO links(source_article_id, target_article_id) VALUES(1, 2);')

    def test_insert_link_from_cache(self):
        conn = MockMySQLConnection()
        view = MySQLBuildView(conn)
        conn.cursor().return_vals['SELECT id FROM articles WHERE title=myTarget;'] = [3];
        view.insert_link(1, 'myTarget')
        view.insert_link(2, 'myTarget')
        self.assertEqual(len(conn.cursor().queries), 3)
        self.assertEqual(conn.cursor().queries[0], 
            'SELECT id FROM articles WHERE title=myTarget;')
        self.assertEqual(conn.cursor().queries[1],
            'INSERT INTO links(source_article_id, target_article_id) VALUES(1, 3);')
        self.assertEqual(conn.cursor().queries[2],
            'INSERT INTO links(source_article_id, target_article_id) VALUES(2, 3);')

    def test_reset_cache(self):
        conn = MockMySQLConnection()
        view = MySQLBuildView(conn)
        conn.cursor().return_vals['SELECT id FROM articles WHERE title=myTarget;'] = [3];
        view.insert_link(1, 'myTarget')
        view.reset_cache()
        view.insert_link(2, 'myTarget')
        self.assertEqual(len(conn.cursor().queries), 4)        

    def test_insert_link_redirect(self):
        conn = MockMySQLConnection()
        view = MySQLBuildView(conn)
        conn.cursor().return_vals['SELECT id FROM articles WHERE title=(SELECT target_article_name FROM redirects WHERE source_article_name=myRedirect);'] = [2];
        view.insert_link(1, 'myRedirect')
        self.assertEqual(len(conn.cursor().queries), 3)
        self.assertEqual(conn.cursor().queries[0], 
            'SELECT id FROM articles WHERE title=myRedirect;')
        self.assertEqual(conn.cursor().queries[1], 
            'SELECT id FROM articles WHERE title=(SELECT target_article_name FROM redirects WHERE source_article_name=myRedirect);')
        self.assertEqual(conn.cursor().queries[2],
            'INSERT INTO links(source_article_id, target_article_id) VALUES(1, 2);')
        
    def test_insert_disambiguation(self):
        conn = MockMySQLConnection()
        view = MySQLBuildView(conn)
        conn.cursor().return_vals['SELECT id FROM articles WHERE title=myTarget;'] = [2];
        view.insert_disambiguation('meaning1', 'myTarget')
        self.assertEqual(len(conn.cursor().queries), 2)
        self.assertEqual(conn.cursor().queries[0], 
            'SELECT id FROM articles WHERE title=myTarget;')
        self.assertEqual(conn.cursor().queries[1],
            'INSERT INTO disambiguations(string, target_article_id, occurrences) VALUES(meaning1, 2, 1) ON DUPLICATE KEY UPDATE occurrences=occurrences+1;')

    def test_insert_ngrams(self):
        conn = MockMySQLConnection()
        view = MySQLBuildView(conn)
        ngrams = [
            ('nolink', 0),
            ('link1', 1),
            ('link link1', 1)
        ]
        view.insert_ngrams(ngrams)
        self.assertEqual(len(conn.cursor().queries), 3)
        self.assertEqual(conn.cursor().queries[0], 
            'INSERT INTO ngrams(string, occurrences, as_link) VALUES(LOWER(nolink), 1, 0) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(conn.cursor().queries[1], 
            'INSERT INTO ngrams(string, occurrences, as_link) VALUES(LOWER(link1), 1, 1) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(conn.cursor().queries[2], 
            'INSERT INTO ngrams(string, occurrences, as_link) VALUES(LOWER(link link1), 1, 1) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')

    def test_commit(self):
        conn = MockMySQLConnection()
        view = MySQLBuildView(conn)
        self.assertEqual(conn.commited, 0)
        view.commit()
        self.assertEqual(conn.commited, 1)

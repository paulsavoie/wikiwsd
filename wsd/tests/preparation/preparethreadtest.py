import unittest
import Queue
import time
from wsd.creator.preparation import PrepareThread

class PrepareThreadTest(unittest.TestCase):
    def setUp(self):
        self._connection = MySQLMockConnection()

    def test_single_article(self):
        queue = Queue.Queue()

        # add entries to queue
        queue.put( { 'id': 1, 'source': 'mySource', 'target': '' } )

        thread = PrepareThread(queue, self._connection)
        thread.start()
        time.sleep(0.1)
        thread.end()
        thread.join()

        self.assertEqual(queue.empty(), True, 'Unexpected item in queue')
        self.assertEqual(len(self._connection.cur.queries), 1)
        self.assertEqual(self._connection.cur.queries[0], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(1, NOW(), mysource, 0);')
        self.assertEqual(self._connection.commit_called, 1)

    def test_single_redirect(self):
        queue = Queue.Queue()

        # add entries to queue
        queue.put( { 'id': 1, 'source': 'mySource', 'target': 'myTarget' } )

        thread = PrepareThread(queue, self._connection)
        thread.start()
        time.sleep(0.1)
        thread.end()
        thread.join()

        self.assertEqual(queue.empty(), True, 'Unexpected item in queue')
        self.assertEqual(len(self._connection.cur.queries), 1)
        self.assertEqual(self._connection.cur.queries[0], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource, mytarget);')
        self.assertEqual(self._connection.commit_called, 1)

    def test_multiple_articles(self):
        queue = Queue.Queue()

        # add entries to queue
        queue.put( { 'id':  1, 'source': 'mySource01', 'target': '' } )
        queue.put( { 'id':  2, 'source': 'mySource02', 'target': '' } )
        queue.put( { 'id':  3, 'source': 'mySource03', 'target': '' } )
        queue.put( { 'id':  4, 'source': 'mySource04', 'target': '' } )
        queue.put( { 'id':  5, 'source': 'mySource05', 'target': '' } )
        queue.put( { 'id':  6, 'source': 'mySource06', 'target': '' } )
        queue.put( { 'id':  7, 'source': 'mySource07', 'target': '' } )
        queue.put( { 'id':  8, 'source': 'mySource08', 'target': '' } )
        queue.put( { 'id':  9, 'source': 'mySource09', 'target': '' } )
        queue.put( { 'id': 10, 'source': 'mySource10', 'target': '' } )
        queue.put( { 'id': 11, 'source': 'mySource11', 'target': '' } )

        thread = PrepareThread(queue, self._connection)
        thread.start()
        time.sleep(0.1)
        thread.end()
        thread.join()

        self.assertEqual(queue.empty(), True, 'Unexpected item in queue')
        self.assertEqual(len(self._connection.cur.queries), 11)
        self.assertEqual(self._connection.cur.queries[0], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(1, NOW(), mysource01, 0);')
        self.assertEqual(self._connection.cur.queries[1], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(2, NOW(), mysource02, 0);')
        self.assertEqual(self._connection.cur.queries[2], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(3, NOW(), mysource03, 0);')
        self.assertEqual(self._connection.cur.queries[3], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(4, NOW(), mysource04, 0);')
        self.assertEqual(self._connection.cur.queries[4], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(5, NOW(), mysource05, 0);')
        self.assertEqual(self._connection.cur.queries[5], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(6, NOW(), mysource06, 0);')
        self.assertEqual(self._connection.cur.queries[6], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(7, NOW(), mysource07, 0);')
        self.assertEqual(self._connection.cur.queries[7], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(8, NOW(), mysource08, 0);')
        self.assertEqual(self._connection.cur.queries[8], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(9, NOW(), mysource09, 0);')
        self.assertEqual(self._connection.cur.queries[9], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(10, NOW(), mysource10, 0);')
        self.assertEqual(self._connection.cur.queries[10], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(11, NOW(), mysource11, 0);')
        self.assertEqual(self._connection.commit_called, 11)

    def test_multiple_redirects(self):
        queue = Queue.Queue()

        # add entries to queue
        queue.put( { 'id':  1, 'source': 'mySource01', 'target': 'myTarget01' } )
        queue.put( { 'id':  2, 'source': 'mySource02', 'target': 'myTarget02' } )
        queue.put( { 'id':  3, 'source': 'mySource03', 'target': 'myTarget03' } )
        queue.put( { 'id':  4, 'source': 'mySource04', 'target': 'myTarget04' } )
        queue.put( { 'id':  5, 'source': 'mySource05', 'target': 'myTarget05' } )
        queue.put( { 'id':  6, 'source': 'mySource06', 'target': 'myTarget06' } )
        queue.put( { 'id':  7, 'source': 'mySource07', 'target': 'myTarget07' } )
        queue.put( { 'id':  8, 'source': 'mySource08', 'target': 'myTarget08' } )
        queue.put( { 'id':  9, 'source': 'mySource09', 'target': 'myTarget09' } )
        queue.put( { 'id': 10, 'source': 'mySource10', 'target': 'myTarget10' } )
        queue.put( { 'id': 11, 'source': 'mySource11', 'target': 'myTarget11' } )

        thread = PrepareThread(queue, self._connection)
        thread.start()
        time.sleep(0.1)
        thread.end()
        thread.join()

        self.assertEqual(queue.empty(), True, 'Unexpected item in queue')
        self.assertEqual(len(self._connection.cur.queries), 11)
        self.assertEqual(self._connection.cur.queries[0], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource01, mytarget01);')
        self.assertEqual(self._connection.cur.queries[1], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource02, mytarget02);')
        self.assertEqual(self._connection.cur.queries[2], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource03, mytarget03);')
        self.assertEqual(self._connection.cur.queries[3], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource04, mytarget04);')
        self.assertEqual(self._connection.cur.queries[4], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource05, mytarget05);')
        self.assertEqual(self._connection.cur.queries[5], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource06, mytarget06);')
        self.assertEqual(self._connection.cur.queries[6], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource07, mytarget07);')
        self.assertEqual(self._connection.cur.queries[7], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource08, mytarget08);')
        self.assertEqual(self._connection.cur.queries[8], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource09, mytarget09);')
        self.assertEqual(self._connection.cur.queries[9], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource10, mytarget10);')
        self.assertEqual(self._connection.cur.queries[10], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource11, mytarget11);')
        self.assertEqual(self._connection.commit_called, 11)

    def test_mixed(self):
        queue = Queue.Queue()

        # add entries to queue
        queue.put( { 'id':  1, 'source': 'mySource01', 'target': '' } )
        queue.put( { 'id':  2, 'source': 'mySource02', 'target': 'myTarget02' } )
        queue.put( { 'id':  3, 'source': 'mySource03', 'target': '' } )
        queue.put( { 'id':  4, 'source': 'mySource04', 'target': 'myTarget04' } )
        queue.put( { 'id':  5, 'source': 'mySource05', 'target': '' } )
        queue.put( { 'id':  6, 'source': 'mySource06', 'target': 'myTarget06' } )
        queue.put( { 'id':  7, 'source': 'mySource07', 'target': '' } )
        queue.put( { 'id':  8, 'source': 'mySource08', 'target': 'myTarget08' } )
        queue.put( { 'id':  9, 'source': 'mySource09', 'target': '' } )
        queue.put( { 'id': 10, 'source': 'mySource10', 'target': 'myTarget10' } )
        queue.put( { 'id': 11, 'source': 'mySource11', 'target': '' } )

        thread = PrepareThread(queue, self._connection)
        thread.start()
        time.sleep(0.1)
        thread.end()
        thread.join()

        self.assertEqual(queue.empty(), True, 'Unexpected item in queue')
        self.assertEqual(len(self._connection.cur.queries), 11)
        self.assertEqual(self._connection.cur.queries[0], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(1, NOW(), mysource01, 0);')
        self.assertEqual(self._connection.cur.queries[2], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(3, NOW(), mysource03, 0);')
        self.assertEqual(self._connection.cur.queries[4], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(5, NOW(), mysource05, 0);')
        self.assertEqual(self._connection.cur.queries[6], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(7, NOW(), mysource07, 0);')
        self.assertEqual(self._connection.cur.queries[8], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(9, NOW(), mysource09, 0);')
        self.assertEqual(self._connection.cur.queries[10], 'INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(11, NOW(), mysource11, 0);')
        self.assertEqual(self._connection.cur.queries[1], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource02, mytarget02);')
        self.assertEqual(self._connection.cur.queries[3], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource04, mytarget04);')
        self.assertEqual(self._connection.cur.queries[5], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource06, mytarget06);')
        self.assertEqual(self._connection.cur.queries[7], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource08, mytarget08);')
        self.assertEqual(self._connection.cur.queries[9], 'INSERT INTO redirects(source_article_name, target_article_name) VALUES(mysource10, mytarget10);')
        self.assertEqual(self._connection.commit_called, 11)

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

class MySQLMockConnection():
    def __init__(self):
        self.cur = MySQLMockCursor()
        self.commit_called = 0

    def cursor(self):
        return self.cur

    def commit(self):
        self.commit_called += 1
import unittest
import Queue
import time
from wsd.creator.preparation import PrepareThread

class PrepareThreadTest(unittest.TestCase):
    def setUp(self):
        self._articles = MockMongoTable()
        self._redirects = MockMongoTable()
        db = MockMongoDB(self._articles, self._redirects)
        self._client = MockMongoClient( databases={ 'myDB': db })

    def test_single_article(self):
        queue = Queue.Queue()

        # add entries to queue
        queue.put( { 'id': 1, 'source': 'mySource', 'target': '' } )

        thread = PrepareThread(queue, self._client, 'myDB')
        thread.start()
        time.sleep(0.1)
        thread.end()
        thread.join()

        self.assertEqual(queue.empty(), True, 'Unexpected item in queue')
        self.assertEqual(self._client.start_request_called, 1)
        self.assertEqual(self._client.end_request_called, 1)
        self.assertEqual(self._redirects.entries, [])
        self.assertEqual(self._redirects.insert_called, 0)
        self.assertEqual(self._articles.entries, [ { 'id': 1, 'title': 'mySource', 'articles_link_here': [] } ])
        self.assertEqual(self._articles.insert_called, 1)

    def test_single_redirect(self):
        queue = Queue.Queue()

        # add entries to queue
        queue.put( { 'id': 1, 'source': 'mySource', 'target': 'myTarget' } )

        thread = PrepareThread(queue, self._client, 'myDB')
        thread.start()
        time.sleep(0.1)
        thread.end()
        thread.join()

        self.assertEqual(queue.empty(), True, 'Unexpected item in queue')
        self.assertEqual(self._client.start_request_called, 1)
        self.assertEqual(self._client.end_request_called, 1)
        self.assertEqual(self._redirects.entries, [{ 'source': 'mySource', 'target': 'myTarget' }])
        self.assertEqual(self._redirects.insert_called, 1)
        self.assertEqual(self._articles.entries, [])
        self.assertEqual(self._articles.insert_called, 0)

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

        thread = PrepareThread(queue, self._client, 'myDB')
        thread.start()
        time.sleep(0.1)
        thread.end()
        thread.join()

        self.assertEqual(queue.empty(), True, 'Unexpected item in queue')
        self.assertEqual(self._client.start_request_called, 1)
        self.assertEqual(self._client.end_request_called, 1)
        self.assertEqual(self._redirects.insert_called, 0)
        self.assertEqual(self._redirects.entries, [])
        self.assertEqual(len(self._articles.entries), 11)
        self.assertEqual(self._articles.insert_called, 2)
        self.assertEqual(self._articles.entries[10], { 'id': 11, 'title': 'mySource11', 'articles_link_here': []})

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

        thread = PrepareThread(queue, self._client, 'myDB')
        thread.start()
        time.sleep(0.1)
        thread.end()
        thread.join()

        self.assertEqual(queue.empty(), True, 'Unexpected item in queue')
        self.assertEqual(self._client.start_request_called, 1)
        self.assertEqual(self._client.end_request_called, 1)
        self.assertEqual(self._redirects.insert_called, 2)
        self.assertEqual(len(self._redirects.entries), 11)
        self.assertEqual(self._articles.entries, [])
        self.assertEqual(self._articles.insert_called, 0)
        self.assertEqual(self._redirects.insert_called, 2)
        self.assertEqual(self._redirects.entries[10], { 'source': 'mySource11', 'target': 'myTarget11'})

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

        thread = PrepareThread(queue, self._client, 'myDB')
        thread.start()
        time.sleep(0.1)
        thread.end()
        thread.join()

        self.assertEqual(queue.empty(), True, 'Unexpected item in queue')
        self.assertEqual(self._client.start_request_called, 1)
        self.assertEqual(self._client.end_request_called, 1)
        self.assertEqual(self._redirects.insert_called, 1)
        self.assertEqual(self._articles.insert_called, 1)
        self.assertEqual(len(self._redirects.entries), 5)
        self.assertEqual(len(self._articles.entries), 6)
        self.assertEqual(self._redirects.entries[4], { 'source': 'mySource10', 'target': 'myTarget10' } )
        self.assertEqual(self._articles.entries[5], { 'id': 11, 'title': 'mySource11', 'articles_link_here': []})

class MockMongoDB():
    def __init__(self, articles, redirects):
        self.articles = articles
        self.redirects = redirects

class MockMongoClient():
    def __init__(self, databases={}):
        self.start_request_called = 0
        self.end_request_called = 0
        self._databases = databases

    def start_request(self):
        self.start_request_called += 1

    def end_request(self):
        self.end_request_called += 1

    def __getitem__(self, k):
        if k in self._databases:
            return self._databases[k]
        raise AttributeError

class MockMongoTable():
    def __init__(self):
        self.entries = []
        self.insert_called = 0

    def insert(self, entry, w=1):
        self.insert_called += 1
        if type( entry ) == list:
            for e in entry:
                self.entries.append(e)
        else:
            self.entries.append(entry)
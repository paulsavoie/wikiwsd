import unittest
import Queue
import time
from wsd.creator.wikiparser import WorkingThread

class WorkingThreadTest(unittest.TestCase):
    def setUp(self):
        self._articles = MockMongoTable()
        self._redirects = MockMongoTable()
        self._meanings = MockMongoTable()
        db = MockMongoDB(self._articles, self._redirects, self._meanings)
        self._client = MockMongoClient( databases={ 'myDB': db })

    def test_queue(self):
        queue = Queue.Queue()
        thread = WorkingThread(queue, self._client, 'myDB')
        thread.start()
        queue.put({ 'id': 123, 'title': 'myTitle', 'text': u''})
        time.sleep(0.01)
        thread.end()
        thread.join()

        self.assertEqual(queue.empty(), True, 'Item in queue')

    def test_processed(self):
        queue = Queue.Queue()
        thread = WorkingThread(queue, self._client, 'myDB')
        thread.start()
        queue.put({ 'id': 123, 'title': 'myTitle', 'text': u'[[a link]]'})
        time.sleep(0.01)
        thread.end()
        thread.join()

        self.assertEqual(self._client.start_request_called, 1)
        self.assertEqual(self._client.end_request_called, 1)
        self.assertNotEqual(self._articles.update_called, 0)
        self.assertNotEqual(self._meanings.update_called, 0)

class MockMongoDB():
    def __init__(self, articles, redirects, meanings):
        self.articles = articles
        self.redirects = redirects
        self.meanings = meanings

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
        self.update_called = 0

    def update(self, selector, update, upsert=False):
        self.update_called += 1

    def find_one(self, selector):
        return {
            'id': 12345,
            'title': selector['title']
        }
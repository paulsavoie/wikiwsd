import unittest
import Queue
import time
from wsd.creator.wikiparser import WorkingThread

class WorkingThreadTest(unittest.TestCase):
    def setUp(self):
        self._connection = MySQLMockConnection()

    def test_queue(self):
        queue = Queue.Queue()
        thread = WorkingThread(queue, self._connection)
        thread.start()
        queue.put({ 'id': 123, 'title': 'myTitle', 'text': u''})
        time.sleep(0.01)
        thread.end()
        thread.join()

        self.assertEqual(queue.empty(), True, 'Item in queue')

    def test_processed(self):
        queue = Queue.Queue()
        thread = WorkingThread(queue, self._connection)
        thread.start()
        queue.put({ 'id': 123, 'title': 'myTitle', 'text': u'[[a link]]'})
        time.sleep(0.01)
        thread.end()
        thread.join()

        self.assertEqual(len(self._connection.cur.queries), 2)
        self.assertEqual(self._connection.cur.queries[0], 'SELECT id, title, articleincount FROM articles WHERE title=a link;')
        self.assertEqual(self._connection.cur.queries[1], 'SELECT target_article_name FROM redirects WHERE source_article_name=a link;')

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

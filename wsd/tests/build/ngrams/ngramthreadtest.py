import unittest
import Queue
import time
from wsd.build.ngrams import NGramThread

class NGramThreadTest(unittest.TestCase):
    def setUp(self):
        self._connection = MySQLMockConnection()

    def test_simple(self):
        queue = Queue.Queue()
        thread = NGramThread(queue, self._connection)
        thread.start()
        text = u'| invalid line\nHere is a [[target article|special link]]\n'
        article = { 'title': u'Test article', 'text': text }
        queue.put(article)
        time.sleep(0.01)
        thread.end()
        thread.join()

        queries = self._connection.cur.queries
        self.assertEqual(len(queries), 15)
        self.assertEqual(queries[0], 'INSERT INTO ngrams_a(string, occurrences, as_link) VALUES(a, 1, 0) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(queries[1], 'INSERT INTO ngrams_a(string, occurrences, as_link) VALUES(a special, 1, 0) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(queries[2], 'INSERT INTO ngrams_a(string, occurrences, as_link) VALUES(a special link, 1, 0) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(queries[3], 'INSERT INTO ngrams_h(string, occurrences, as_link) VALUES(Here, 1, 0) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(queries[4], 'INSERT INTO ngrams_h(string, occurrences, as_link) VALUES(Here is, 1, 0) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(queries[5], 'INSERT INTO ngrams_h(string, occurrences, as_link) VALUES(Here is a, 1, 0) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(queries[6], 'INSERT INTO ngrams_h(string, occurrences, as_link) VALUES(Here is a special, 1, 0) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(queries[7], 'INSERT INTO ngrams_h(string, occurrences, as_link) VALUES(Here is a special link, 1, 0) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(queries[8], 'INSERT INTO ngrams_i(string, occurrences, as_link) VALUES(is, 1, 0) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(queries[9], 'INSERT INTO ngrams_i(string, occurrences, as_link) VALUES(is a, 1, 0) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(queries[10], 'INSERT INTO ngrams_i(string, occurrences, as_link) VALUES(is a special, 1, 0) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(queries[11], 'INSERT INTO ngrams_i(string, occurrences, as_link) VALUES(is a special link, 1, 0) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(queries[12], 'INSERT INTO ngrams_l(string, occurrences, as_link) VALUES(link, 1, 0) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(queries[13], 'INSERT INTO ngrams_s(string, occurrences, as_link) VALUES(special, 1, 0) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')
        self.assertEqual(queries[14], 'INSERT INTO ngrams_s(string, occurrences, as_link) VALUES(special link, 1, 1) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);')

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
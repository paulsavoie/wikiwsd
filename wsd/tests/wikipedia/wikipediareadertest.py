import unittest
import Queue
from wsd.wikipedia import WikipediaReader

class WikipediaReaderTest(unittest.TestCase):

    def test_redirect(self):
        queue = Queue.Queue()
        reader = WikipediaReader('./wsd/tests/data/single3.xml', queue)
        reader.start()
        reader.join()
        expect = {
            'type': 'redirect',
            'id': 10,
            'title': 'AccessibleComputing',
            'target': 'Computer accessibility',
            'text': ''
        }
        self.assertEqual(reader.articles_parsed(), 1)
        self.assertEqual(queue.empty(), False)
        item = queue.get()
        self.assertEqual(item, expect)

    def test_single_article(self):
        queue = Queue.Queue()
        reader = WikipediaReader('./wsd/tests/data/single4.xml', queue)
        reader.start()
        reader.join()
        expect = {
            'type': 'article',
            'id': 12,
            'title': 'Anarchism',
            'target': '',
            'text': 'This is a dummy text\nwith multiple lines'
        }
        self.assertEqual(reader.articles_parsed(), 1)
        self.assertEqual(queue.empty(), False)
        item = queue.get()
        self.assertEqual(item, expect)

    def test_single_article_no_text(self):
        queue = Queue.Queue()
        reader = WikipediaReader('./wsd/tests/data/single4.xml', queue, False)
        reader.start()
        reader.join()
        expect = {
            'type': 'article',
            'id': 12,
            'title': 'Anarchism',
            'target': '',
            'text': ''
        }
        self.assertEqual(reader.articles_parsed(), 1)
        self.assertEqual(queue.empty(), False)
        item = queue.get()
        self.assertEqual(item, expect)

    def test_multiple_articles(self):
        queue = Queue.Queue()
        reader = WikipediaReader('./wsd/tests/data/multiple2.xml', queue)
        reader.start()
        reader.join()
        expect1 = {
            'type': 'article',
            'id': 12,
            'title': 'Anarchism',
            'target': '',
            'text': 'This is a dummy text\nwith multiple lines'
        }
        expect2 = {
            'type': 'article',
            'id': 123456,
            'title': 'Dummy Title',
            'target': '',
            'text': 'This is a dummy text.'
        }
        expect3 = {
            'type': 'redirect',
            'id': 10,
            'title': 'AccessibleComputing',
            'target': 'Computer accessibility',
            'text': ''
        }
        self.assertEqual(reader.articles_parsed(), 3)
        self.assertEqual(queue.empty(), False)
        item1 = queue.get()
        self.assertEqual(item1, expect1)
        self.assertEqual(queue.empty(), False)
        item2 = queue.get()
        self.assertEqual(item2, expect2)
        self.assertEqual(queue.empty(), False)
        item3 = queue.get()
        self.assertEqual(item3, expect3)

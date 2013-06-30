import unittest
import Queue
import xml.sax
from wsd.creator.wikiparser import Reader

class ReaderTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_normal_article(self):
        queue = Queue.Queue()
        reader = Reader(queue)
        xml.sax.parse('wsd/tests/data/single1.xml', reader)

        self.assertEqual(queue.empty(), False, 'No item in queue')
        article = queue.get()
        self.assertEqual(queue.empty(), True, 'More than one item in queue')
        self.assertEqual(article['id'], 12, 'Article ID wrong')
        self.assertEqual(article['title'], u'Anarchism', 'Title is wrong')
        self.assertEqual(article['text'][:100], u'{{Redirect|Anarchist|the fictional character|Anarchist (comics)}}\n{{Redirect|Anarchists}}\n{{Use dmy ', 'Text is wrong')

    def test_redirect(self):
        queue = Queue.Queue()
        reader = Reader(queue)
        xml.sax.parse('wsd/tests/data/single3.xml', reader)

        self.assertEqual(queue.empty(), True, 'Wrong item in queue')


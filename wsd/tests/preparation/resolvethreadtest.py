import unittest
import Queue
from wsd.creator.preparation import ResolveThread

class ResolveThreadTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_normal_article(self):
        queue = Queue.Queue()
        thread = ResolveThread('wsd/tests/data/single1.xml', queue)
        thread.start()
        thread.join()

        self.assertEqual(queue.empty(), False, 'No item in queue')
        article = queue.get()
        self.assertEqual(queue.empty(), True, 'More than one item in queue')
        self.assertEqual(article['id'], 12, 'Article ID wrong')
        self.assertEqual(article['source'], u'Anarchism', 'Title is wrong')
        self.assertEqual(article['target'], u'', 'Target article wrong')

    def test_redirect(self):
        queue = Queue.Queue()
        thread = ResolveThread('wsd/tests/data/single3.xml', queue)
        thread.start()
        thread.join()

        self.assertEqual(queue.empty(), False, 'No item in queue')
        article = queue.get()
        self.assertEqual(queue.empty(), True, 'More than one item in queue')
        self.assertEqual(article['id'], 10, 'Article ID wrong')
        self.assertEqual(article['source'], u'AccessibleComputing', 'Source article wrong')
        self.assertEqual(article['target'], u'Computer accessibility', 'Target article wrong')


import unittest
import Queue
from wsd.creator.wikiparser import ReadingThread

class ReadingThreadTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_queue(self):
        queue = Queue.Queue()
        thread = ReadingThread('wsd/tests/data/single1.xml', queue)
        thread.start()
        thread.join()

        self.assertEqual(queue.empty(), False, 'No item in queue')


import time
import threading
import xml.sax
import Queue
from reader import Reader

class ReadingThread(threading.Thread):
    def __init__(self, path, article_queue):
        threading.Thread.__init__(self)
        self._reader = Reader(article_queue)
        self._path = path

    def run(self):
        xml.sax.parse(self._path, self._reader)


if __name__ == '__main__':
    time.clock()
    thread = ReadingThread('../data/training.xml', Queue.Queue())
    thread.start()
    thread.join()
    print time.clock()

import time
import threading
import xml.sax
from reader import Reader

class ReadingThread(threading.Thread):
    def __init__(self, path):
        threading.Thread.__init__(self)
        self._reader = Reader()
        self._path = path

    def run(self):
        xml.sax.parse(self._path, self._reader)


if __name__ == '__main__':
    time.clock()
    thread = ReadingThread('../data/training.xml')
    thread.start()
    thread.join()
    print time.clock()

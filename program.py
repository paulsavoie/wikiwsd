"""The main program
"""

import time
import Queue
from wikiparser import WorkingThread
from wikiparser import ReadingThread

class Program():
    def __init__(self, xml_path, max_queue_size=10):
        self._queue = Queue.Queue(maxsize=max_queue_size)
        self._reading_thread = ReadingThread(xml_path, self._queue)
        self._working_thread = WorkingThread(self._queue)

    def run(self):
        self._reading_thread.start()
        self._working_thread.start()
        # wait until there is something in the queue
        while self._queue.empty():
            pass
        self._queue.join()
        self._working_thread.end()
        self._working_thread.join()
        self._reading_thread.join()


if __name__ == '__main__':
    prog = Program('data/training.xml')
    time.clock()
    prog.run()
    print time.clock()

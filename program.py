"""The main program
"""

import time
import Queue
import MySQLdb as mysqldb
from wikiparser import WorkingThread
from wikiparser import ReadingThread

class Program():
    def __init__(self, xml_path, db_connection=None, max_queue_size=10):
        self._queue = Queue.Queue(maxsize=max_queue_size)
        self._reading_thread = ReadingThread(xml_path, self._queue)
        self._working_thread1 = WorkingThread(self._queue, db_connection)
        self._working_thread2 = WorkingThread(self._queue, db_connection)
        self._working_thread3 = WorkingThread(self._queue, db_connection)

    def run(self):
        self._reading_thread.start()
        self._working_thread1.start()
        self._working_thread2.start()
        self._working_thread3.start()
        # wait until there is something in the queue
        while self._queue.empty():
            pass
        self._queue.join()
        self._working_thread1.end()
        self._working_thread2.end()
        self._working_thread3.end()
        self._working_thread1.join()
        self._working_thread2.join()
        self._working_thread3.join()
        self._reading_thread.join()


if __name__ == '__main__':
    try:
        con = mysqldb.connect('localhost', 'wikiwsd', 'wikiwsd', 'wikiwsd')
        prog = Program('data/training.xml', con)
        time.clock()
        prog.run()
        print time.clock()
    except mysqldb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])

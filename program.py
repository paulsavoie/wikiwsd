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
        self._working_thread = WorkingThread(self._queue, db_connection)

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
    try:
        con = mysqldb.connect('localhost', 'wikiwsd', 'wikiwsd', 'wikiwsd')
        prog = Program('data/single2.xml', con)
        time.clock()
        prog.run()
        print time.clock()
    except mysqldb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])

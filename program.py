"""The main program
"""

import time
import Queue
import MySQLdb as mysqldb
from wikiparser import WorkingThread
from wikiparser import ReadingThread

class Program():
    def __init__(self, xml_path, max_queue_size=10, num_threads=1, 
            db_host='localhost', db_user='wikiwsd', db_pass='wikiwsd'):
        self._queue = Queue.Queue(maxsize=max_queue_size)
        self._reading_thread = ReadingThread(xml_path, self._queue)
        self._worker_threads = []
        for i in range (0, num_threads):
            con = mysqldb.connect(db_host, db_user, db_pass, 'wikiwsd', charset='utf8', use_unicode=True)
            self._worker_threads.append(WorkingThread(self._queue, con))

    def run(self):
        self._reading_thread.start()
        for worker in self._worker_threads:
            worker.start()
        # wait until there is something in the queue
        while self._queue.empty():
            pass
        self._queue.join()
        for worker in self._worker_threads:
            worker.end()
        for worker in self._worker_threads:
            worker.join()
        self._reading_thread.join()


if __name__ == '__main__':
    try:
        prog = Program('/home/paul/data/wikipedia/enwiki-20130102-pages-articles.xml', num_threads=8)
        time.clock()
        prog.run()
        print time.clock()
    except mysqldb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])

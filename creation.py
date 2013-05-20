"""The main program
"""

import time
import Queue
import MySQLdb as mysqldb
import MySQLdb.cursors
from wikiparser import WorkingThread
from wikiparser import ReadingThread
from preparation import ResolveThread
from preparation import PrepareThread

class Creator():
    def __init__(self, xml_path, max_queue_size=20, num_threads=1, 
            db_host='localhost', db_user='wikiwsd', db_pass='wikiwsd', action='learn'):
        self._queue = Queue.Queue(maxsize=max_queue_size)
        if action == 'learn':
            self._reading_thread = ReadingThread(xml_path, self._queue)
            self._worker_threads = []
            for i in range (0, num_threads):
                con = mysqldb.connect(db_host, db_user, db_pass, 'wikiwsd2', charset='utf8', use_unicode=True)
                self._worker_threads.append(WorkingThread(self._queue, con))
        elif action == 'prepare':
            self._reading_thread = ResolveThread(xml_path, self._queue)
            self._worker_threads = []
            for i in range (0, num_threads):
                con = mysqldb.connect(db_host, db_user, db_pass, 'wikiwsd2', charset='utf8', use_unicode=True)
                self._worker_threads.append(PrepareThread(self._queue, con))

    def run(self):
        self._reading_thread.start()
        for worker in self._worker_threads:
            worker.start()
	# wait until all articles are read
	self._reading_thread.join()

        # wait for all articles to be processed
        self._queue.join()
        for worker in self._worker_threads:
            worker.end()
        for worker in self._worker_threads:
            worker.join()


if __name__ == '__main__':
    try:
        # first action 'prepare' to learn links
        # then action 'learn' to learn
        prog = Creator('/home/paul/data/wikipedia/enwiki-20130102-pages-articles.xml', num_threads=26, max_queue_size=300, action='learn')
        #prog = Creator('data/training.xml', num_threads=25, max_queue_size=300, db_host='10.11.0.103', action='learn')
        time.clock()
        prog.run()
        print time.clock()
    except mysqldb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])

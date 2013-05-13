"""The main program
"""

import time
import Queue
import MySQLdb as mysqldb
import MySQLdb.cursors
from wikiparser import WorkingThread
from wikiparser import ReadingThread
from updater import SelectThread
from updater import UpdateThread

class Program():
    def __init__(self, xml_path, max_queue_size=20, num_threads=1, 
            db_host='10.0.0.1', db_user='wikiwsd', db_pass='wikiwsd', action='learn'):
        self._queue = Queue.Queue(maxsize=max_queue_size)
        if action == 'learn':
            self._reading_thread = ReadingThread(xml_path, self._queue)
            self._worker_threads = []
            for i in range (0, num_threads):
                con = mysqldb.connect(db_host, db_user, db_pass, 'wikiwsd', charset='utf8', use_unicode=True)
                self._worker_threads.append(WorkingThread(self._queue, con))
        elif action == 'update':
            con_select = mysqldb.connect(db_host, db_user, db_pass, 'wikiwsd', charset='utf8', use_unicode=True, cursorclass=MySQLdb.cursors.SSCursor)
            self._reading_thread = SelectThread(self._queue, con_select)
            self._worker_threads = []
            for i in range (0, num_threads):
                con = mysqldb.connect(db_host, db_user, db_pass, 'wikiwsd', charset='utf8', use_unicode=True)
                self._worker_threads.append(UpdateThread(self._queue, con))

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
        prog = Program('/home/paul/data/wikipedia/enwiki-20130102-pages-articles.xml', num_threads=52, max_queue_size=100, action='update')
        time.clock()
        prog.run()
        print time.clock()
    except mysqldb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])

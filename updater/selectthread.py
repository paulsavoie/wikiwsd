"""A thread wrapper for the sql selector
"""

import time
import threading
import Queue
import MySQLdb as mysqldb

class SelectThread(threading.Thread):
    def __init__(self, link_queue, db_connection=None):
        threading.Thread.__init__(self)
        self._db_connection = db_connection
        self._link_queue = link_queue

    def run(self):
        if self._db_connection:
            cur = self._db_connection.cursor()
            # iterate over each article
            cur.execute('SELECT id, article_id, target_article FROM links;')
            counter = 0
            for row in cur:
                # add target title to queue
                #print 'added link "%s"' % (row[0])
                self._link_queue.put((row[1], row[2]))
                counter = counter + 1
                if counter % 100 == 0:
                    print 'added %d links' % counter

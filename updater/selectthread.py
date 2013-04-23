"""A thread wrapper for the sql selector
"""

import time
import threading
import Queue

class SelectThread(threading.Thread):
    def __init__(self, link_queue, db_connection=None):
        threading.Thread.__init__(self)
        self._db_connection = db_connection
        self._link_queue = link_queue

    def run(self):
        if self._db_connection:
            cur = self._db_connection.cursor()
            # iterate over each article
            cur.execute('SELECT * FROM links;')
            numrows = int(cur.rowcount)
            for i in range(numrows):
                row = cur.fetchone()
                # add target title to queue
                link_queue.put(row[3])

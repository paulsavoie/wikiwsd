"""A thread wrapper for the parser
"""

import time
import threading
import Queue

class UpdateThread(threading.Thread):
    def __init__(self, link_queue, db_connection=None):
        threading.Thread.__init__(self)
        self._db_connection = db_connection
        self._queue = link_queue
        self._end = False

    def run(self):
        while not self._end:
            try:
                title = self._queue.get(True, 2)
                print 'updating article "%s"' % title
                cur = self._db_connection.cursor()
                cur.execute('UPDATE articles SET linkincount = linkincount + 1 WHERE title="%s"' % (title))
                self._db_connection.commit()
            except Queue.Empty:
                pass

    def end(self):
        self._end = True

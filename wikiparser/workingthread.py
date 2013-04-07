"""A thread wrapper for the parser
"""

import time
import threading
import Queue
from wikiparser import WikiParser

class WorkingThread(threading.Thread):
    def __init__(self, article_queue, db_connection=None):
        threading.Thread.__init__(self)
        self._parser = WikiParser(db_connection)
        self._queue = article_queue
        self._end = False

    def run(self):
        while not self._end:
            try:
                article = self._queue.get(True, 2)
                print 'parsing article %s' % (article['title'])
                self._parser.parse_article(article)
                self._queue.task_done()
            except Queue.Empty:
                pass

    def end(self):
        self._end = True

"""A thread wrapper for the parser
"""

import time
import threading
import Queue
from wikiparser import WikiParser

class WorkingThread(threading.Thread):
    def __init__(self, article_queue, client, database):
        threading.Thread.__init__(self)
        self._parser = WikiParser(client, database)
        self._queue = article_queue
        self._client = client
        self._end = False

    def run(self):
        self._client.start_request()
        while not self._end:
            try:
                article = self._queue.get(True, 2)
                print 'parsing article %s' % (article['title'].encode('ascii', 'ignore'))
                self._parser.parse_article(article)
                self._queue.task_done()
            except Queue.Empty:
                pass
        self._client.end_request()

    def end(self):
        self._end = True

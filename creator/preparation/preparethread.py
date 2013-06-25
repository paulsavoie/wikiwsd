"""A thread wrapper for the parser
"""

import time
import threading
import Queue
import pymongo

class PrepareThread(threading.Thread):
    def __init__(self, redirect_queue, client, database):
        threading.Thread.__init__(self)
        self._client = client
        self._db = client[database]
        self._queue = redirect_queue
        self._article_bulk = []
        self._redirect_bulk = []
        self._end = False

    def __save_bulks(self):
        try:
            if len(self._article_bulk) > 0:
                self._db.articles.insert(self._article_bulk, w=1)
            if len(self._redirect_bulk) > 0:
                self._db.redirects.insert(self._redirect_bulk, w=1)
            #print 'successfully inserted: %s' % (self._article_bulk[0]['title'].encode('ascii', 'ignore'))
        except pymongo.errors.DuplicateKeyError, e:
            print 'ERROR: DuplicateKeyError: %s' % (str(e))
        finally:
            self._redirect_bulk = []
            self._article_bulk = []

    def run(self):
        self._client.start_request()
        while not self._end:
            try:
                vals = self._queue.get(True, 2)
                source_name = vals['source']
                target_name = vals['target']
                article_id = vals['id']

                if len(target_name) == 0:
                    self._article_bulk.append( { "id": article_id, "title": source_name, "articles_link_here": [] } )
                else:
                    self._redirect_bulk.append( { "source": source_name, "target": target_name })

                if len(self._article_bulk) > 30 or len(self._redirect_bulk) > 30:
                    self.__save_bulks()

                self._queue.task_done()
            except Queue.Empty:
                pass

        self.__save_bulks()
        self._client.end_request()

    def end(self):
        self._end = True

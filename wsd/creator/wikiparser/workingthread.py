# -*- coding: utf-8 -*-
'''
This file contains the wrapper class that starts
the parsing process of the read wikipedia articles

Author: Paul Laufer
Date: Jun 2013

'''

import time
import threading
import Queue
from wikiparser import WikiParser
import logging

class WorkingThread(threading.Thread):
    '''Thread wrapper to parse separate articles from the queue 
    '''

    '''constructor

    Arguments:
        article_queue --- the queue with the read articles
        client --- the mongodb client instance
        db_name --- the name of the database to use
    '''
    def __init__(self, article_queue, client, db_name):
        threading.Thread.__init__(self)
        self._parser = WikiParser(client, db_name)
        self._queue = article_queue
        self._client = client
        self._end = False

    def run(self):
        self._client.start_request()
        while not self._end:
            try:
                article = self._queue.get(True, 2)
                logging.info('parsing article %s' % (article['title'].encode('ascii', 'ignore')))
                self._parser.parse_article(article)
                self._queue.task_done()
            except Queue.Empty:
                pass
        self._client.end_request()

    '''ends the thread 
    '''
    def end(self):
        self._end = True

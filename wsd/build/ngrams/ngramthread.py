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
from ngramparser import NGramParser
import logging

class NGramThread(threading.Thread):
    '''Thread wrapper to parse separate articles from the queue 
    '''

    '''constructor

    Arguments:
        article_queue --- the queue with the read articles
        client --- the mongodb client instance
        db_name --- the name of the database to use
    '''
    def __init__(self, article_queue, db_connection):
        threading.Thread.__init__(self)
        self._parser = NGramParser(db_connection)
        self._queue = article_queue
        self._end = False

    def run(self):
        while not self._end:
            try:
                article = self._queue.get(True, 2)
                logging.info('parsing article %s' % (article['title'].encode('ascii', 'ignore')))
                self._parser.parse_article(article)
                self._parser.extract_n_grams(article)
                self._queue.task_done()
            except Queue.Empty:
                pass

    '''ends the thread 
    '''
    def end(self):
        self._end = True

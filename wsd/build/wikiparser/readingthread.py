# -*- coding: utf-8 -*-
'''
This file contains the wrapper class that starts
the reading process of the wikipedia dump file

Author: Paul Laufer
Date: Jun 2013

'''

import time
import threading
import xml.sax
import Queue
from reader import Reader

class ReadingThread(threading.Thread):
    '''thread wrapper to read articles using a Reader instance
    '''

    '''constructor

    Arguments:
        xml_path --- the path to the wikipedia dump file
        article_queue - the queue to which the articles shall be read to
    '''
    def __init__(self, xml_path, article_queue):
        threading.Thread.__init__(self)
        self._reader = Reader(article_queue)
        self._path = xml_path

    def run(self):
        xml.sax.parse(self._path, self._reader)

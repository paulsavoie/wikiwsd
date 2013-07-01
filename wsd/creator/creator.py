# -*- coding: utf-8 -*-
'''
This file contains the code to initiate the building
process of the database

Author: Paul Laufer
Date: Jun 2013

'''

import time
import Queue
from pymongo import MongoClient
from wikiparser import WorkingThread
from wikiparser import ReadingThread
from preparation import ResolveThread
from preparation import PrepareThread

class Creator():
    ''' class that handles the building process of the database
    '''

    '''constructor

    Arguments:
        xml_path --- the path to the wikipedia dump file
        max_queue-size --- the maximum number of articles to hold in memory at any time (default to 20)
        num_threads --- the number of processing threads to use (defaults to 1)
        db_host --- the host name of the database (default to 'localhost')
        db_port --- the port number of the database server (defaults to 27017)
        action --- the action to perform, either 'prepare' or 'learn' (defaults to 'learn')
    '''
    def __init__(self, xml_path, max_queue_size=20, num_threads=1, 
            db_host='localhost', db_port=27017, action='learn'):
        self._queue = Queue.Queue(maxsize=max_queue_size)
        client = MongoClient(db_host, db_port, auto_start_request=True)
        if action == 'learn':
            self._reading_thread = ReadingThread(xml_path, self._queue)
            self._worker_threads = []
            for i in range (0, num_threads):
                #client = MongoClient(db_host, db_port)
                self._worker_threads.append(WorkingThread(self._queue, client ,'wikiwsd'))
        elif action == 'prepare':
            self._reading_thread = ResolveThread(xml_path, self._queue)
            self._worker_threads = []
            for i in range (0, num_threads):
                #client = MongoClient(db_host, db_port)
                self._worker_threads.append(PrepareThread(self._queue, client, 'wikiwsd'))

    '''starts the building process of the database
    '''
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

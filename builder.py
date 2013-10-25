# -*- coding: utf-8 -*-
'''
This file contains the code which allows to easily
build and prepare the database used for the disambiguation library

Author: Paul Laufer
Date: Oct 2013

'''

import os
import time
import logging
import Queue
from wsd.database import MySQLDatabase
from wsd.wikipedia import WikipediaReader
from wsd.wikipedia import WikipediaPreProcessor
from wsd.wikipedia import NGramExtractor
from wsd.build import ArticleInserter
from wsd.build import DisambiguationInserter
from wsd.build import NGramInserter
from consoleapp import ConsoleApp
from dbsettings import *

class BuilderApp(ConsoleApp):
    '''The EvaluationApp class is a console application to facilitate
       the building process
    '''

    def __init__(self):
        pass

    def run(self):
        self.print_title('This is the interactive building program')
        self.create_tmp_if_not_exists()

        choice = self.read_choice('Would you like to', [
            'create the database structure', 
            'extract articles and redirects from the wikipedia dump file',
            'parse the wikipedia dump file and extract links and disambiguations',
            'parse the wikipedia dump file and extract ngrams for link detection',
            'optimize the database'
            ])

        # setup logging
        LOGGING_FORMAT = '%(levelname)s:\t%(asctime)-15s %(message)s'
        LOGGING_PATH = self.read_path('Please enter the path of the logging file [.log]', default='./tmp/build-%d.log' % (choice[0]+1), must_exist=False)
        logging.basicConfig(filename=LOGGING_PATH, level=logging.DEBUG, format=LOGGING_FORMAT, filemode='w')

        if choice[0] == 0:
            self._create_structure()
        elif choice[0] == 1:
            self._extract_articles()
        elif choice[0] == 2:
            self._extract_disambiguations()
        elif choice[0] == 3:
            self._extract_ngrams()
        else:
            self._optimize_database()

    def _create_structure(self):

        # measure time
        start = time.clock()

        # creating structure
        db = MySQLDatabase(DATABASE_HOST, DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME)
        db.build()

        seconds = round (time.clock() - start)
        print 'Finished after %02d:%02d minutes' % (seconds / 60, seconds % 60)

    def _extract_articles(self):

        INPUT_FILE = self.read_path('Please enter the path of the wiki dump file [.xml]')
        MAX_ARTICLES_IN_QUEUE = self.read_number('How many articles should be kept in the memory at any time at most?', 200, 20, 300)
        NUM_THREADS = self.read_number('How many threads shall be used to write to the database?', 20, 1, 50)
        CONTINUE = self.read_yes_no('This process might take several days to finish.\nDo you want to continue?')

        if CONTINUE:
            # measure time
            start = time.clock()

            # connect to database and create article queue
            db = MySQLDatabase(DATABASE_HOST, DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME)
            queue = Queue.Queue(maxsize=MAX_ARTICLES_IN_QUEUE)

            # create reader and threads
            reader = WikipediaReader(INPUT_FILE, queue, extract_text=False)
            threads = []
            for i in range(0, NUM_THREADS):
                inserter = ArticleInserter(queue, db.get_build_view())
                threads.append(inserter)

            # start reader
            reader.start()

            # start insert threads
            for thread in threads:
                thread.start()

            # wait for reading thread, queue and inserters to be done
            reader.join()
            queue.join()
            for thread in threads:
                thread.end()
            for thread in threads:
                thread.join()

            seconds = round (time.clock() - start)
            print 'Finished after %02d:%02d minutes' % (seconds / 60, seconds % 60)

        else:
            print 'Aborting...'

    def _extract_disambiguations(self):

        INPUT_FILE = self.read_path('Please enter the path of the wiki dump file [.xml]')
        MAX_ARTICLES_IN_QUEUE = self.read_number('How many articles should be kept in the memory at any time at most?', 200, 20, 300)
        NUM_THREADS = self.read_number('How many threads shall be used to write to the database?', 20, 1, 50)
        CONTINUE = self.read_yes_no('This process might take several days to finish.\nDo you want to continue?')

        if CONTINUE:
            # measure time
            start = time.clock()

            # connect to database and create article queue
            db = MySQLDatabase(DATABASE_HOST, DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME)
            queue = Queue.Queue(maxsize=MAX_ARTICLES_IN_QUEUE)

            # create reader and threads
            reader = WikipediaReader(INPUT_FILE, queue)
            threads = []
            for i in range(0, NUM_THREADS):
                inserter = DisambiguationInserter(queue, db.get_build_view())
                threads.append(inserter)

            # start reader
            reader.start()

            # start insert threads
            for thread in threads:
                thread.start()

            # wait for reading thread, queue and inserters to be done
            reader.join()
            queue.join()
            for thread in threads:
                thread.end()
            for thread in threads:
                thread.join()

            seconds = round (time.clock() - start)
            print 'Finished after %02d:%02d minutes' % (seconds / 60, seconds % 60)
            
        else:
            print 'Aborting...'

    def _extract_ngrams(self):

        INPUT_FILE = self.read_path('Please enter the path of the wiki dump file [.xml]')
        MAX_ARTICLES_IN_QUEUE = self.read_number('How many articles should be kept in the memory (times 3) at any time at most?', 100, 20, 300)
        CONTINUE = self.read_yes_no('This process might take several days to finish.\nDo you want to continue?')

        if CONTINUE:
            # measure time
            start = time.clock()

             # connect to database and create article queue
            db = MySQLDatabase(DATABASE_HOST, DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME)
            queue1 = Queue.Queue(maxsize=MAX_ARTICLES_IN_QUEUE)
            queue2 = Queue.Queue(maxsize=MAX_ARTICLES_IN_QUEUE)
            queue3 = Queue.Queue(maxsize=MAX_ARTICLES_IN_QUEUE)

            # create reader, preprocessor, ngramextractor and inserter
            reader = WikipediaReader(INPUT_FILE, queue1)
            preprocessor = WikipediaPreProcessor(queue1, queue2)
            ngramextractor = NGramExtractor(queue2, queue3)
            inserter = NGramInserter(queue3, db.get_build_view())

            # start instances
            reader.start()
            preprocessor.start()
            ngramextractor.start()
            inserter.start()

            # wait for queues and isntances
            reader.join()
            queue1.join()
            queue2.join()
            queue3.join()

            preprocessor.end()
            ngramextractor.end()
            inserter.end()

            preprocessor.join()
            ngramextractor.join()
            inserter.join()

            seconds = round (time.clock() - start)
            print 'Finished after %02d:%02d minutes' % (seconds / 60, seconds % 60)
            
        else:
            print 'Aborting...'

    def _optimize_database(self):

        CONTINUE = self.read_yes_no('This process might take several hours to finish.\nDo you want to continue?')

        if CONTINUE:
            # measure time
            start = time.clock()

            # optimizing database
            # creating structure
            db = MySQLDatabase(DATABASE_HOST, DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME)
            db.optimize()

            seconds = round (time.clock() - start)
            print 'Finished after %02d:%02d minutes' % (seconds / 60, seconds % 60)
            
        else:
            print 'Aborting...'

if __name__ == '__main__':
    runner = BuilderApp()
    runner.run()
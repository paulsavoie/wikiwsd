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
from wsd.database import MySQLDatabase
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

        print 'TODO: create database structure'

        seconds = round (time.clock() - start)
        print 'Finished after %02d:%02d minutes' % (seconds / 60, seconds % 60)

    def _extract_articles(self):

        INPUT_FILE = self.read_path('Please enter the path of the wiki dump file [.xml]')
        CONTINUE = self.read_yes_no('This process might take several days to finish.\nDo you want to continue?')

        if CONTINUE:
            # measure time
            start = time.clock()

            print 'TODO: extract articles and redirects'

            seconds = round (time.clock() - start)
            print 'Finished after %02d:%02d minutes' % (seconds / 60, seconds % 60)

        else:
            print 'Aborting...'

    def _extract_disambiguations(self):

        INPUT_FILE = self.read_path('Please enter the path of the wiki dump file [.xml]')
        CONTINUE = self.read_yes_no('This process might take several days to finish.\nDo you want to continue?')

        if CONTINUE:
            # measure time
            start = time.clock()

            print 'TODO: extract links and disambiguations'

            seconds = round (time.clock() - start)
            print 'Finished after %02d:%02d minutes' % (seconds / 60, seconds % 60)
            
        else:
            print 'Aborting...'

    def _extract_ngrams(self):

        INPUT_FILE = self.read_path('Please enter the path of the wiki dump file [.xml]')
        CONTINUE = self.read_yes_no('This process might take several days to finish.\nDo you want to continue?')

        if CONTINUE:
            # measure time
            start = time.clock()

            print 'TODO: extract ngrams'

            seconds = round (time.clock() - start)
            print 'Finished after %02d:%02d minutes' % (seconds / 60, seconds % 60)
            
        else:
            print 'Aborting...'

    def _optimize_database(self):

        CONTINUE = self.read_yes_no('This process might take several hours to finish.\nDo you want to continue?')

        if CONTINUE:
            # measure time
            start = time.clock()

            print 'TODO: optimize'

            seconds = round (time.clock() - start)
            print 'Finished after %02d:%02d minutes' % (seconds / 60, seconds % 60)
            
        else:
            print 'Aborting...'

if __name__ == '__main__':
    runner = BuilderApp()
    runner.run()
# -*- coding: utf-8 -*-
'''
This file contains the code which allows the easy usage
of the disambiguation library

Author: Paul Laufer
Date: Jun 2013

'''

import os
import time
import logging
from wsd.database import MySQLDatabase
from wsd.evaluation import Evaluator
from wsd.evaluation import SampleReader
from consoleapp import ConsoleApp
from dbsettings import *

class EvaluationApp(ConsoleApp):
    '''The EvaluationApp class is a console application to facilitate
       the evaluation process
    '''

    def __init__(self):
        pass

    def run(self):
        self.print_title('This is the interactive evaluation program')
        self.create_tmp_if_not_exists()

        choice = self.read_choice('Would you like to', ['read samples from the wiki dump file', 'evaluate the samples'])

        if choice[0] == 0:
            self._read_samples()
        else:
            self._evaluate_samples()

    def _read_samples(self):
        INPUT_FILE = self.read_path('Please enter the path of the wiki dump file [.xml]')
        OUTPUT_FILE = self.read_path('Please enter the path of the output samples file [.xml]', default='./tmp/samples.xml', must_exist=False)
        LOGGING_PATH = self.read_path('Please enter the path of the logging file [.log]', default='./tmp/evaluation1.log', must_exist=False)
        NUM_SAMPLES = self.read_number('Select the number of samples to use for the evaluation', default=1)

        CONTINUE = self.read_yes_no('This process might take from some seconds to some minutes.\nDo you want to continue?')

        if not CONTINUE:
            print '# Aborting...'
            return

        print '# Starting to read samples...'
        # setup logging
        LOGGING_FORMAT = '%(levelname)s:\t%(asctime)-15s %(message)s'
        logging.basicConfig(filename=LOGGING_PATH, level=logging.DEBUG, format=LOGGING_FORMAT, filemode='w')

        # measure time
        start = time.clock()

        # read samples
        reader = SampleReader(INPUT_FILE, NUM_SAMPLES, OUTPUT_FILE)
        reader.read()

        seconds = round (time.clock() - start)
        print 'Finished after %02d:%02d minutes' % (seconds / 60, seconds % 60)

    def _evaluate_samples(self):
        INPUT_FILE = self.read_path('Please enter the path of the samples file [.xml]', default='./tmp/samples.xml')
        LOGGING_PATH = self.read_path('Please enter the path of the logging file [.log]', default='./tmp/evaluation2.log', must_exist=False)
        
        CONTINUE = self.read_yes_no('This process might take from several minutes to several hours.\nDo you want to continue?')

        if not CONTINUE:
            print '# Aborting...'
            return

        print '# Starting evaluation...'
        # setup logging
        LOGGING_FORMAT = '%(levelname)s:\t%(asctime)-15s %(message)s'
        logging.basicConfig(filename=LOGGING_PATH, level=logging.DEBUG, format=LOGGING_FORMAT, filemode='w')

        # connecting to db
        db = MySQLDatabase(DATABASE_HOST, DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME)
        work_view = db.get_work_view()

        evaluator = Evaluator(INPUT_FILE, work_view)
        result = evaluator.run()

        seconds = round (time.clock() - start)
        print 'Finished after %02d:%02d minutes' % (seconds / 60, seconds % 60)
        print 'Evaluation done! - precision: %d%%, recall: %d%%' % (round(result['precision']*100), round(result['recall']*100))

if __name__ == '__main__':
    runner = EvaluationApp()
    runner.run()
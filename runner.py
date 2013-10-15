# -*- coding: utf-8 -*-
'''
This file contains the code which allows the easy usage
of the disambiguation library

Author: Paul Laufer
Date: Jun 2013

'''

import time
import logging
import Queue
from wsd.database import MySQLDatabase
from wsd.algorithm import MeaningFinder
from wsd.algorithm import RelatednessCalculator
from wsd.algorithm import Decider
from wsd.algorithm import LinkDetector
from wsd.runner import TermIdentifier
from wsd.runner import HTMLOutputter
from consoleapp import ConsoleApp
from dbsettings import *

class RunnerApp(ConsoleApp):
    '''The RunnerApp is a console application to facilitate the
       usage of the wsd library
    '''

    def __init__(self):
        pass

    def run(self):
        self.print_title('This is the interactive runner program')
        self.create_tmp_if_not_exists()

        INPUT_FILE = self.read_path('Please enter the path of the input file [.txt]', default='./tmp/input.txt')
        OUTPUT_FILE = self.read_path('Please enter the path of the output file [.html]', default='./tmp/output.html', must_exist=False)
        LOGGING_PATH = self.read_path('Please enter the path of the logging file [.log]', default='./tmp/runner.log', must_exist=False)


        print '# Starting runner...'
        # setup logging
        LOGGING_FORMAT = '%(levelname)s:\t%(asctime)-15s %(message)s'
        logging.basicConfig(filename=LOGGING_PATH, level=logging.DEBUG, format=LOGGING_FORMAT, filemode='w')

        # measure time
        start = time.clock()

        # connect to db
        db = MySQLDatabase(DATABASE_HOST, DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME)
        work_view = db.get_work_view()

        # read input
        f = open(INPUT_FILE, 'r')
        text = f.read()
        text = text.replace('&nbsp;', ' ')
        f.close()

        # create dummy article
        article = {}
        article['type'] = 'article'
        article['id'] = None
        article['title'] = None
        article['text'] = text
        article['links'] = []

        # identify links
        link_detector = LinkDetector(work_view)
        link_detector.detect_links(article)
        # identify terms
        #term_identifier = TermIdentifier()
        #article = term_identifier.identify_terms(text)

        # find possible meanings
        meaning_finder = MeaningFinder(work_view)
        meaning_finder.find_meanings(article)

        # calculate relatedness
        relatedness_calculator = RelatednessCalculator(work_view)

        # decide for meaning
        decider = Decider(relatedness_calculator)
        decider.decide(article)

        # output results
        html_outputter = HTMLOutputter()
        html_outputter.output(article, OUTPUT_FILE)

        seconds = round (time.clock() - start)
        print 'Finished after %02d:%02d minutes' % (seconds / 60, seconds % 60)

if __name__ == '__main__':
    runner = RunnerApp()
    runner.run()
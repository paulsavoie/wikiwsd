# -*- coding: utf-8 -*-
'''
This file contains the code which allows the easy usage
of the disambiguation library

Author: Paul Laufer
Date: Jun 2013

'''

import time
import logging
import MySQLdb as mysqldb
from wsd import TermIdentifier
from wsd import MeaningFinder
from wsd import CommonnessRetriever 
from wsd import RelatednessCalculator
from wsd import Decider
from wsd import HTMLOutputter
from wsd import MySQLConnector 

LOGGING_FORMAT = '%(levelname)s:\t%(asctime)-15s %(message)s'

class MainProgram():
    '''this class glues together the different parts of the wsd library to model
    the whole disambiguation process
    '''

    '''constructor

    Arguments:
        db_connector --- the database connector (an instance of wsd.DBConnector)
        input_file --- the path to the text file to be disambiguated
        output_file --- the path of the html output file containing the disambiguation 
    '''
    def __init__(self, db_connector, input_file='data/simpleinput.txt', output_file='data/simpleoutput.html'):
        self._db_connector = db_connector
        self._input_file = input_file
        self._output_file = output_file

    '''runs the actual disambiguation process
    '''
    def run(self):
        f = open(self._input_file, 'r')
        text = f.read()
        text = text.replace('&nbsp;', ' ')
        f.close()

        termIdentifier = TermIdentifier(self._db_connector)
        words = termIdentifier.identify_terms(text)

        meaningFinder = MeaningFinder(self._db_connector)
        disambiguations = meaningFinder.find_meanings(words)

        commonnessRetriever = CommonnessRetriever(self._db_connector)
        relatednessCalculator = RelatednessCalculator(commonnessRetriever)

        decider = Decider(relatednessCalculator)
        decider.decide(words)

        outputter = HTMLOutputter()
        outputter.output(words, self._output_file)


if __name__ == '__main__':
    try:
        dbConnector = MySQLConnector('localhost')
        logging.basicConfig(filename='running.log', level=logging.DEBUG, format=LOGGING_FORMAT, filemode='w')
        prog = MainProgram(db_connector=dbConnector)
        time.clock()
        prog.run()
        total = round(time.clock())
        minutes = total / 60
        seconds = total % 60
        print 'Finished in %d minutes and %d seconds' % (minutes, seconds)
    except mysqldb.Error, e:
        print e
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
from wsd.runner import TermIdentifier
from wsd.runner import HTMLOutputter

# setup logging
LOGGING_FORMAT = '%(levelname)s:\t%(asctime)-15s %(message)s'
logging.basicConfig(filename='running.log', level=logging.DEBUG, format=LOGGING_FORMAT, filemode='w')

# measure time
start = time.clock()

# connect to db
db = MySQLDatabase()
work_view = db.get_work_view()

# read input
INPUT_FILE = 'data/simpleinput.txt'
f = open(INPUT_FILE, 'r')
text = f.read()
text = text.replace('&nbsp;', ' ')
f.close()

# identify terms
term_identifier = TermIdentifier()
article = term_identifier.identify_terms(text)

# find possible meanings
meaning_finder = MeaningFinder(work_view)
meaning_finder.find_meanings(article)

# calculate relatedness
relatedness_calculator = RelatednessCalculator(work_view)

# decide for meaning
decider = Decider(relatedness_calculator)
decider.decide(article)

# output results
OUTPUT_FILE = 'data/simpleoutput.html'
html_outputter = HTMLOutputter()
html_outputter.output(article, OUTPUT_FILE)

seconds = round (time.clock() - start)
print 'Finished in %02d:%02d minutes' % (seconds / 60, seconds % 60)

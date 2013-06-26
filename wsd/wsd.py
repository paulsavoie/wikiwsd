"""The main program
"""

import time
import MySQLdb as mysqldb
from termidentifier import TermIdentifier
from meaningfinder import MeaningFinder
from commonnessretriever import CommonnessRetriever 
from relatednesscalculator import RelatednessCalculator
from decider import Decider
from outputter import HTMLOutputter
from mysqlconnector import MySQLConnector 

class WordSenseDisambiguator():
    def __init__(self, db_connector, input_file='../data/simpleinput.txt', output_file='../data/simpleoutput.html'):
        self._db_connector = db_connector
        self._input_file = input_file
        self._output_file = output_file

    def run(self):
        f = open(self._input_file, 'r')
        text = f.read()
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
        prog = WordSenseDisambiguator(db_connector=dbConnector)
        time.clock()
        prog.run()
        total = round(time.clock())
        minutes = total / 60
        seconds = total % 60
        print 'Finished in %d minutes and %d seconds' % (minutes, seconds)
    except mysqldb.Error, e:
        print e
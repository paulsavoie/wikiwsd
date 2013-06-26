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

class WordSenseDisambiguator():
    def __init__(self, input_file='../data/simpleinput.txt', output_file='../data/simpleoutput.html',
            db_host='localhost', db_user='wikiwsd', db_pass='wikiwsd'):
        self._db_connection = mysqldb.connect(db_host, db_user, db_pass, 'wikiwsd3', charset='utf8', use_unicode=True)
        self._input_file = input_file
        self._output_file = output_file

    def run(self):
        f = open(self._input_file, 'r')
        text = f.read()
        f.close()

        termIdentifier = TermIdentifier(self._db_connection)
        words = termIdentifier.identify_terms(text)

        meaningFinder = MeaningFinder(self._db_connection)
        disambiguations = meaningFinder.find_meanings(words)

        commonnessRetriever = CommonnessRetriever(self._db_connection)
        relatednessCalculator = RelatednessCalculator(commonnessRetriever)

        decider = Decider(relatednessCalculator)
        decider.decide(words)

        outputter = HTMLOutputter()
        outputter.output(words, self._output_file)


if __name__ == '__main__':
    try:
        prog = WordSenseDisambiguator(db_host='localhost')
        time.clock()
        prog.run()
        total = round(time.clock())
        minutes = total / 60
        seconds = total % 60
        print 'Finished in %d minutes and %d seconds' % (minutes, seconds)
    except mysqldb.Error, e:
        print e
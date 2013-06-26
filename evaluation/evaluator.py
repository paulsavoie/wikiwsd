import logging
import json
import MySQLdb as mysqldb
from wsd import MeaningFinder
from wsd import CommonnessRetriever 
from wsd import RelatednessCalculator
from wsd import Decider
from outputter import EvaluationOutputter

class Evaluator():

    def __init__(self, inputFile, db_host='localhost', db_port=27017):
        self._input_path = inputFile
        self._db_host = db_host
        self._db_port = db_port

    def run(self):
        # read json file
        f = open(self._input_path, 'r')
        samples = json.JSONDecoder().decode(f.read())
        f.close()

        # terms are already identified

        # TODO: temporary connect to mysql db - change with upgrade to mongodb
        db_connection = mysqldb.connect('localhost', 'wikiwsd', 'wikiwsd', 'wikiwsd3', charset='utf8', use_unicode=True)

        total = 0.0
        correct = 0.0
        for sample in samples:
            words = sample['terms']
            # TODO: modify meaningFinder to only retrieve reduced meanings
            meaningFinder = MeaningFinder(db_connection)
            disambiguations = meaningFinder.find_meanings(words)

            # TODO: modify commonnessRetriever to only retrieve reduced commonness
            commonnessRetriever = CommonnessRetriever(db_connection)
            relatednessCalculator = RelatednessCalculator(commonnessRetriever)

            decider = Decider(relatednessCalculator)
            decider.decide(words)

            # TODO: create evaluation outputter
            outputter = EvaluationOutputter()
            results = outputter.output(words)
            total += results['total']
            correct += results['correct']

        return correct / total
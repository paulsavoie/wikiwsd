import logging
import json

class Evaluator():

    def __init__(self, inputFile, db_host='localhost', db_port=27017):
        self._input_path = inputFile
        self._db_host = db_host
        self._db_port = db_port

    def run(self):
        # read json file
        f = open(self._input_path, 'r')
        samples = json.JSONDecoder(f.read())
        f.close()

        # terms are already identified

        # TODO: modify meaningFinder to only retrieve reduced meanings
        meaningFinder = MeaningFinder(self._db_connection)
        disambiguations = meaningFinder.find_meanings(words)

        # TODO: modify commonnessRetriever to only retrieve reduced commonness
        commonnessRetriever = CommonnessRetriever(self._db_connection)
        relatednessCalculator = RelatednessCalculator(commonnessRetriever)

        decider = Decider(relatednessCalculator)
        decider.decide(words)

        # TODO: create evaluation outputter
        outputter = HTMLOutputter()
        outputter.output(words, self._output_file)

        return 0.0
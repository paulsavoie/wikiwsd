import logging
import json
import MySQLdb as mysqldb
from wsd import MeaningFinder
from wsd import CommonnessRetriever 
from wsd import RelatednessCalculator
from wsd import Decider
from wsd import MySQLConnector
from outputterold import EvaluationOutputterOld
from connector import EvaluationConnector
import logging

class EvaluatorOld():

    def __init__(self, inputFile, db_host='localhost', db_port=27017):
        self._input_path = inputFile
        self._db_host = db_host
        self._db_port = db_port

    def run(self):
        # read json file
        f = open(self._input_path, 'r')
        content = f.read()
        content = content.replace('&nbsp;', ' ')
        samples = json.JSONDecoder().decode(content)
        f.close()

        # terms are already identified

        # TODO: temporary connect to mysql db - change with upgrade to mongodb
        db_connector = MySQLConnector('localhost')

        total = 0.0
        correct = 0.0
        for sample in samples:
            words = sample['terms']
            links = sample['links']

            logging.info('starting to evaluate sample %s' % sample['title'])

            # update the correct meaning in case of redirects
            for word in words:
                if word.has_key('original'):
                    original = word['original']
                    real_name = db_connector.resolve_redirect(original)
                    if real_name != None:
                        word['original'] = real_name
                        # update links
                        if links.has_key(original):
                            links[real_name] = links[original]
                            del links[original]
                    # strip word - is done by wordpuncttokenizer in normal run
                    word['token'] = word['token'].strip(' ,.:;-!"\'')


            evaluation_connector = EvaluationConnector(db_connector, sample)

            # TODO: modify meaningFinder to only retrieve reduced meanings
            meaningFinder = MeaningFinder(evaluation_connector)
            disambiguations = meaningFinder.find_meanings(words)

            # TODO: modify commonnessRetriever to only retrieve reduced commonness
            commonnessRetriever = CommonnessRetriever(evaluation_connector)
            relatednessCalculator = RelatednessCalculator(commonnessRetriever)

            decider = Decider(relatednessCalculator)
            decider.decide(words)

            # TODO: create evaluation outputter
            outputter = EvaluationOutputterOld()
            results = outputter.output(words)
            total += results['total']
            correct += results['correct']
            rate = float(results['correct']) / float(results['total'])
            logging.info('evaluated sample %s: got %d%% correct', sample['title'], round(rate*100))

        logging.info('done evaluating %d samples' % len(samples))

        return correct / total
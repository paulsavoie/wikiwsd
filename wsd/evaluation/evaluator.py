import logging
import Queue
from wsd.database import MySQLDatabase
from wsd.algorithm import MeaningFinder, RelatednessCalculator, RelatednessRetriever, Decider
from workview import EvaluationWorkView
from outputter import EvaluationOutputter
from wsd.wikipedia import WikipediaReader, WikipediaPreProcessor, LinkExtractor

class Evaluator():

    def __init__(self, inputFile):
        self._input_path = inputFile

    def run(self):
        # connect to db
        db = MySQLDatabase()
        orig_work_view = db.get_work_view()

        # read sample
        article_queue = Queue.Queue()
        reader = WikipediaReader(self._input_path, article_queue)
        preprocessor = WikipediaPreProcessor()
        linkextractor = LinkExtractor(orig_work_view)

        reader.start()
        reader.join()
        articles = []
        while article_queue.empty() == False:
            article = article_queue.get()
            preprocessor.process(article)
            linkextractor.process(article)
            articles.append(article)

        # do actual evaluation
        total = 0.0
        correct = 0.0
        for article in articles:
            # wrap work view in evaluation
            work_view = EvaluationWorkView(db.get_work_view(), article)

            logging.info('starting to evaluate sample %s' % article['title'])

            # start for each sample from the beginning
            work_view.reset_cache()

            meaningFinder = MeaningFinder(work_view)
            meaningFinder.find_meanings(article)

            relatednessCalculator = RelatednessCalculator(work_view)

            decider = Decider(relatednessCalculator)
            decider.decide(article)

            outputter = EvaluationOutputter()
            results = outputter.output(article)

            total += results['total']
            correct += results['correct']
            rate = float(results['correct']) / float(results['total'])
            logging.info('evaluated sample %s: got %d%% correct', article['title'], round(rate*100))

        logging.info('done evaluating %d samples' % len(articles))
        return correct / total
import Queue
import threading
from wsd.wikipedia import WikipediaPreProcessor
from wsd.wikipedia import NGramExtractor

MAX_WAIT_QUEUE_TIMEOUT = 2

class NGramInserter(threading.Thread):
    '''Thread which inserts links and disambiguations into the database
    '''

    def __init__(self, queue, build_view):
        threading.Thread.__init__(self)
        '''constructor

           @param queue the queue to which the articles are read
           @param build_view the database build view to use to connect to the database
        '''

        self._queue = queue
        self._build_view = build_view
        self._preprocessor = WikipediaPreProcessor()
        self._extractor = NGramExtractor()
        self._end = False

    def run(self):
        while not self._end:
            
            try:
                # fetch article from queue
                article = self._queue.get(True, MAX_WAIT_QUEUE_TIMEOUT)

                # extract links
                self._preprocessor.process(article)
                ngrams = self._extractor.process(article)

                self._build_view.insert_ngrams(ngrams)

                # commit changes
                self._build_view.commit()

                # reset cache and mark as done
                self._build_view.reset_cache()
                self._queue.task_done()

            except Queue.Empty:
                pass

    def end(self):
        self._end = True
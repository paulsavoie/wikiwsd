import Queue
import threading
from wsd.wikipedia import WikipediaPreProcessor
from wsd.wikipedia import LinkExtractor

MAX_WAIT_QUEUE_TIMEOUT = 2

class DisambiguationInserter(threading.Thread):
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
        self._extractor = LinkExtractor(None)
        self._end = False

    def run(self):
        while not self._end:
            try:
                # fetch article from queue
                article = self._queue.get(True, MAX_WAIT_QUEUE_TIMEOUT)

                if article['type'] == 'article':
                    # extract links
                    self._preprocessor.process(article)
                    self._extractor.process(article)

                    # insert links into database
                    referenced_articles = []
                    for link in article['links']:

                        referenced_article = self._build_view.insert_link(article['id'], link['target_article_name'])
                        self._build_view.insert_disambiguation(link['phrase'], link['target_article_name'])
                        if referenced_article != None:
                            referenced_articles.append(referenced_article)

                        # commit changes
                        self._build_view.commit()

                    # update articleincount in target articles
                    referenced_articles = set(referenced_articles)
                    self._build_view.insert_references(referenced_articles)
                    self._build_view.commit()

                    # reset cache and mark as done
                    self._build_view.reset_cache()
                self._queue.task_done()

            except Queue.Empty:
                pass

    def end(self):
        self._end = True
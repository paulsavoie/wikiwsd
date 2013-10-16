import threading
import Queue
import logging
import re

WAIT_QUEUE_TIMEOUT = 2 # in seconds
MAX_NGRAM_LENGTH = 3

class NGramExtractor(threading.Thread):
    '''The NGramExtractor class extracts ngrams from an article and returns them
    '''

    '''constructor

       @param input_queue if the extractor is used as a thread, articles are read from this queue [optional]
       @param output_queue if the extractor is used as a thread, ngrams are written to this queue [optional]
    '''
    def __init__(self, input_queue=None, output_queue=None):
        threading.Thread.__init__(self)
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._end = False

    '''processes a single article and extracts ngrams

       @param article a dictionary with a text field that contains the text

       @return a list of tuples holding ngrams and a boolean value which is 1 if the ngrams is used as a link
    '''
    def process(self, article):
        ngrams = []

        lines = article['text'].strip().split('\n')
        for line in lines:

            # remove the targets from the links
            line = self._remove_link_targets(line)

            phrases = re.split(r"[!#$%&*+./:;<=>?@\^_`{}~()]", line)
            for phrase in phrases:
                phrase = phrase.strip()
                if len(phrase) > 1:
                    words = phrase.split(' ')
                    # extract ngrams
                    for size in range(1, MAX_NGRAM_LENGTH+1):
                        start = 0
                        while start < len(words) - size + 1:
                            ngram = ''
                            for i in range (0, size):
                                ngram += words[start+i] + ' '
                            ngram = ngram.strip(' ,.:!?=_-')
                            is_link = 0
                            # if there is one link around the whole ngram and no link inside
                            if len(ngram) > 4 and ngram[0:2] == '[[' and ngram[-2:] == ']]' and ngram.find(']]') > ngram.find('[[', 2):
                                is_link = 1
                            ngram = ngram.replace('[[', '')
                            ngram = ngram.replace(']]', '')
                            start+= 1

                            if len(ngram) > 0:
                                ngrams.append((ngram, is_link))

        return ngrams


    '''the main thread method - should not be called, use start() instead
    '''
    def run(self):
        while not self._end:
            try:
                # retrieve a new article from the queue
                article = self._input_queue.get(True, WAIT_QUEUE_TIMEOUT)
                # process the article
                logging.info('extracting ngrams from article %s' % (article['title'].encode('ascii', 'ignore')))
                ngrams = self.process(article)
                # add the ngrams to the output queue
                self._output_queue.put(ngrams)
                # mark the task as done
                self._input_queue.task_done()
            except Queue.Empty:
                pass

    '''ends the thread 
    '''
    def end(self):
        self._end = True

    def _remove_link_targets(self, line):
        # remove link targets
        index = 0
        while line.find('[[', index) != -1:
            index = line.find('[[', index)+2
            end = line.find(']]', index)
            middle = line.find('|', index)
            following = line.find('[[', index)
            # if there is a separator within this link
            if middle != -1 and middle < end:
                # if the separator is before a possible inner link or there is no inner link
                if following == -1 or following > end or following > middle:
                    line = line[0:index] + line[middle+1:]
        return line


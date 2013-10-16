import threading
import Queue
import logging
import re

WAIT_QUEUE_TIMEOUT = 2 # in seconds
MAX_NGRAM_LENGTH = 5

class LinkExtractor(threading.Thread):
    '''The LinkExtractor class extracts link targets from an article and leaves the text with marked link positions
    '''

    '''constructor

       @param work_view a database work used to resolve redirects and extract target article ids (if None, then they will not be resolved)
       @param input_queue if the extractor is used as a thread, articles are read from this queue [optional]
       @param output_queue if the extractor is used as a thread, articles with links are written to this queue [optional]
    '''
    def __init__(self, work_view, input_queue=None, output_queue=None):
        threading.Thread.__init__(self)
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._work_view = work_view
        self._end = False

    '''processes a single article and extracts links

       @param article a dictionary with a text field that contains the text (will be stripped of extra link targets)
                      and extended by a 'links' field containing a list of dictionaries with the following fields:
                        'target_article_id': the id of the target article (none if could not be resolved)
                        'phrase': the phrase used within the link
                        'target_article_name': the name of the target article (None if could not be resolved)
    '''
    def process(self, article):
        links = []
        new_text = ''
        lines = article['text'].strip().split('\n')
        for line in lines:

            index = 0
            while line.find('[[', index) != -1:
                index = line.find('[[', index)+2 # now points to beginning of target / link
                # get correct ending
                end = line.find(']]', index)
                inner = line.find('[[', index)
                while inner != -1 and inner < end:
                    end = line.find(']]', end+2)
                    inner = line.find('[[', inner+2)
                link = line[index-2:end+2]
                (target, phrase) = self._parse_link(link)
                line = line[:index] + phrase + line[end:]
                if len(target) == 0 or len(phrase) == 0:
                    logging.warning('Invalid link in article %s: %s' % (article['title'].encode('ascii', 'ignore'), link.encode('ascii', 'ignore')))
                resolved = self._resolve_link(target, phrase)
                links.append(resolved)

            new_text += line + '\n'
                    
        article['text'] = new_text
        article['links'] = links
        return article

    '''the main thread method - should not be called, use start() instead
    '''
    def run(self):
        while not self._end:
            try:
                # retrieve a new article from the queue
                article = self._input_queue.get(True, WAIT_QUEUE_TIMEOUT)
                # process the article
                logging.info('extracting ngrams from article %s' % (article['title'].encode('ascii', 'ignore')))
                self.process(article)
                # add the ngrams to the output queue
                self._output_queue.put(article)
                # mark the task as done
                self._input_queue.task_done()
            except Queue.Empty:
                pass

    '''ends the thread 
    '''
    def end(self):
        self._end = True

    def _resolve_link(self, target, phrase):
        if self._work_view != None:
            result = self._work_view.resolve_title(target)
            if result == None:
                target_article_id = None
                target_article_name = None
            else:
                target_article_id = result['id']
                target_article_name = result['title']
        else:
            target_article_id = None
            target_article_name = target

        link = {
            'target_article_id': target_article_id,
            'target_article_name': target_article_name,
            'phrase': phrase
        }
        return link

    def _parse_link(self, link):
        target = None
        phrase = ''
        separator = link.find('|')
        inner_start = link.find('[[', 2)
        inner_end = link.rfind(']]', 0, -2)
        # if there is a separator in the most outer link, the target is there
        if separator != -1 and (inner_start == -1 or separator < inner_start):
            target = link[2:separator]
            # if there is an inner link, take first part and then the resolved inner link, then the rest
            if inner_start != -1 and inner_end != -1:
                phrase = link[separator+1:inner_start] + self._parse_link(link[inner_start:inner_end+2])[1] + link[inner_end+2:-2]
            # if there is no inner link, just take the phrase
            else:
                phrase = link[separator+1:-2]
        # if there is no separator in the most outer link, phrase and target are the same
        else:
            if inner_start != -1 and inner_end != -1:
                phrase = link[2:inner_start] + self._parse_link(link[inner_start:inner_end+2])[1] + link[inner_end+2:]
            else:
                phrase = link[2:-2]
            target = phrase

        if phrase.find('[[') != -1 or phrase.find(']]') != -1 or target.find('[[') != -1 or target.find(']]') != -1:
            return ('', '')
        return (target, phrase)

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


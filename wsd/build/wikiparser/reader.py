# -*- coding: utf-8 -*-
'''
This file holds the code to read articles from the Wikipedia 
Dump file in order to create the database entries necessary
for disambiguation

Author: Paul Laufer
Date: Jun 2013

'''

import time
import xml.sax
import Queue
import logging

class Reader(xml.sax.handler.ContentHandler):
    """A SAX Content handler that reads articles from the Wikipedia dump file
    """

    """constructor

    Arguments:
        article_queue --- the queue that the articles will be put to
    """
    def __init__(self, article_queue):
        self._reset_article()
        self._current_tag = u''
        self._queue = article_queue
        self._id_done = False

    def _reset_article(self):
        self._article = {
            'title': u'',
            'id': u'',
            'text': u''
        }
        self._id_done = False

    def startElement(self, name, attrs):
        self._current_tag = name

    def characters(self, content):
        if self._current_tag == 'title':
            self._article['title'] += content
        elif self._current_tag == 'id' and not self._id_done:
            self._article['id'] += content
        elif self._current_tag == 'text':
            self._article['text'] += content

    def endElement(self, name):
        self._current_tag = u''
        # only first id is article id, latter one is revision id
        if name == 'id':
            self._id_done = True
        elif name == 'page':
            if self._article['text'][:len('#REDIRECT')] != '#REDIRECT' and self._article['title'].find(u':') == -1:
                self._current_tag = u''
                try:
                    self._article['id'] = long(self._article['id'])
                    # throw away all articles with ':' in titles (are 
                    # most likely files, categories, etc.)
                    if self._article['title'].find(':') == -1:
                        self._queue.put(self._article)
                except ValueError:
                    logging.error('Article "%s" could not be parsed, as %d is not a valid integer id' % (self._article['title'].encode('ascii', 'ignore'), self._article['id']))
            self._reset_article()

"""A thread wrapper for the xml reader
"""

import time
import threading
import xml.sax
import Queue
import logging

class Resolver(xml.sax.handler.ContentHandler):
    def __init__(self, redirect_queue):
        self._queue = redirect_queue
        self._reset_redirect()
        self._current_tag = u''
        self._article_counter = 0
        self._id_done = False

    def _reset_redirect(self):
        self._redirect = {
            'source': u'',
            'target': u'',
            'id': u''
        }
        self._id_done = False

    def startElement(self, name, attrs):
        self._current_tag = name
        if self._current_tag == 'redirect':
            if not 'title' in attrs.getNames():
                logging.warning('Attribute "title" not in redirect tag of article "%s"' % (self._redirect['source'].encode('ascii', 'ignore')))
            self._redirect['target'] = attrs.getValue('title')

    def characters(self, content):
        if self._current_tag == 'title':
            self._redirect['source'] += content
        elif self._current_tag == 'id' and not self._id_done:
            self._redirect['id'] += content

    def endElement(self, name):
        self._current_tag = u''
        if name == 'id': # only first id is article id, latter one is revision id
            self._id_done = True
        if name == 'page':
            self._article_counter += 1
            if len(self._redirect['source']) > 0 and self._redirect['source'].find(u':') == -1:
                try:
                    self._redirect['id'] = long(self._redirect['id'])
                    self._queue.put(self._redirect)
                except ValueError:
                    logging.error('Article "%s" could not be parsed, as %s is not a valid integer id' % (self._redirect['source'].encode('ascii', 'ignore'), self._redirect['id']))
            self._reset_redirect()
            if self._article_counter % 1000 == 0:
                logging.info('%d articles parsed' % (self._article_counter))

class ResolveThread(threading.Thread):
    def __init__(self, xml_path, redirect_queue):
        threading.Thread.__init__(self)
        self._reader = Resolver(redirect_queue)
        self._path = xml_path

    def run(self):
        xml.sax.parse(self._path, self._reader)


if __name__ == '__main__':
    time.clock()
    thread = ResolveThread('../data/training.xml', Queue.Queue())
    thread.start()
    thread.join()
    print time.clock()

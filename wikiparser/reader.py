"""An xml parser that adds wikipedia articles to a queue
"""

import time
import xml.sax
import Queue

class Reader(xml.sax.handler.ContentHandler):
    def __init__(self, article_queue):
        self._reset_article()
        self._current_tag = u''
        self._queue = article_queue

    def _reset_article(self):
        self._article = {
            'title': u'',
            'id': u'',
            'text': u''
        }

    def startElement(self, name, attrs):
        self._current_tag = name

    def characters(self, content):
        if self._current_tag == 'title':
            self._article['title'] += content
        elif self._current_tag == 'id':
            self._article['id'] += content
        elif self._current_tag == 'text':
            self._article['text'] += content

    def endElement(self, name):
        self._current_tag = u''
        if name == 'page':
            if self._article['text'][:len('#REDIRECT')] != '#REDIRECT':
                self._current_tag = u''
                try:
                    article['id'] = int(article['id'])
                    self._queue.put(self._article)
                except ValueError:
                    print 'Article "%s" could not be parsed, as %d is not a valid integer id' % (article['title'], article['id'])
            self._reset_article()


if __name__ == '__main__':
    time.clock()
    queue = Queue.Queue()
    reader = Reader(queue)
    xml.sax.parse('../data/training.xml', reader)
    counter = 1
    while not queue.empty():
        article = queue.get()
        print '%08d: %r' % (counter, article['title'])
        counter += 1
    print time.clock()
    print counter

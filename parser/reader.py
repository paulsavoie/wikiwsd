import time
import xml.sax

class Reader(xml.sax.handler.ContentHandler):
    """SAX Handler which will store selected attribute values."""
    def __init__(self):
        self.counter = 0
        self._reset_article()
        self._current_tag = u''

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
                print '%08d: %r' % (self.counter, self._article['title'])
                self._current_tag = u''
                self.counter = self.counter + 1
            self._reset_article()


if __name__ == '__main__':
    time.clock()
    reader = Reader()
    xml.sax.parse('../data/training.xml', reader)
    print time.clock()
    print reader.counter

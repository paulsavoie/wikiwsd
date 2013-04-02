import time
import xml.sax

class Reader(xml.sax.handler.ContentHandler):
    """SAX Handler which will store selected attribute values."""
    def __init__(self, target_attrs=()):
        self.target_attrs = target_attrs
        self.counter = 0
	self._current_title = u''
        self._in_title = False

    def startElement(self, name, attrs):
        if name == 'page':
            self.counter = self.counter + 1
        elif name == 'title':
            self._in_title = True 

    def characters(self, content):
        if self._in_title:
            self._current_title += content

    def endElement(self, name):
        if name == 'title':
            print '%08d: %r' % (self.counter, self._current_title)
            self._in_title = False
            self._current_title = u''


if __name__ == '__main__':
    time.clock()
    grabber = Reader(target_attrs=('page'))
    xml.sax.parse('../data/training.xml', grabber)
    print time.clock()
    print grabber.counter

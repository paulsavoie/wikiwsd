import time
import xml.sax

class Reader(xml.sax.handler.ContentHandler):
    """SAX Handler which will store selected attribute values."""
    def __init__(self, target_attrs=()):
        self.target_attrs = target_attrs
        self.counter = 0

    def startElement(self, name, attrs):
        if name == 'page':
            print attrs.get('title', u'')
            self.counter = self.counter + 1

if __name__ == '__main__':
    time.clock()
    grabber = Reader(target_attrs=('page'))
    xml.sax.parse('/home/paul/data/wikipedia/enwiki-20130102-pages-articles.xml', grabber)
    print time.clock()
    print grabber.counter

from lxml import etree

# Parts of this code are taken from
# http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
# Author: Liza Daly

class Reader:
    def __init__(self, wikipedia_file):
        self._wikipedia_file = open(wikipedia_file, 'r')
        self._counter = 0

    def __del__(self):
        self._wikipedia_file.close()

    def process_article(self, elem):
        print elem.xpath( 'title/text( )' )
        self._counter = self._counter + 1

    def read_article(self, context):
        for event, elem in context:
            self._process_article(elem)
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
        del context

    def read(self):
        context = etree.iterparse(self._wikipedia_file, tag='page')
        self.process_article(context)

if __name__ == '__main__':
    time.clock()
    reader = Reader('/home/paul/data/wikipedia/enwiki-20130102-pages-articles.xml')
    reader.read()
    print time.clock()

import logging
import xml.sax
import random
import json
from wikitermidentifier import WikiTermIdentifier

class SampleReader:
    def __init__(self, path, numSamples, output):
        self.__path = path
        self.__num_samples = numSamples
        self.__output_path = output
        self.__xml_reader = XMLSampleReader(self)
        self.__samples = {}
        self.__term_identifier = WikiTermIdentifier()

    def read(self):
        # read from actual file
        f = open(self.__path, 'r')
        f.seek(0, 2) # go to the end of the file
        totalbytes = f.tell()
        max_end = round(float(f.tell())*0.8) # only go to 80% to make sure another sample follows

        for sample in range(0, self.__num_samples):
            # generate random number and go to file point
            start = random.randint(0, max_end)
            f.seek(start, 0)
            foundPage = False
            validPage = False
            xmlString = ''
            while not validPage:
                line = f.readline()
                if line.strip() == '<page>':
                    xmlString += line
                    foundPage = True
                if foundPage:
                    while line.strip() != '</page>':
                        line = f.readline()
                        xmlString+= line

                    # now we got a full xml article
                    oldCount = len(self.__samples)
                    xml.sax.parseString(xmlString, self.__xml_reader)
                    xmlString = ''
                    if oldCount < len(self.__samples):
                        validPage = True

        f.close()
        # store samples in output file
        logging.info('Read %d samples from input file' % len(self.__samples))

        # parse the text
        output = []
        for sample in self.__samples.values():
            article_id = sample['id']
            article_title = sample['title']
            logging.info('Identifying terms in article %s' % article_title)
            identified = self.__term_identifier.identify_terms(sample['text'])
            output.append( { "id": article_id, "title": article_title, "links": identified['links'], 'terms' : identified['terms'] } )

        output_f = open(self.__output_path, 'w')
        output_f.write(json.JSONEncoder().encode(output))
        output_f.close()
        logging.info('Saved samples in JSON file %s' % (self.__output_path))


    def add_article(self, article):
        self.__samples[article['id']] = article


class XMLSampleReader(xml.sax.handler.ContentHandler):
    def __init__(self, reader):
        self.__reader = reader
        self._reset_article()
        self._current_tag = u''
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
                    
                    # notify reader
                    self.__reader.add_article(self._article)

                except ValueError:
                    logging.error('Article "%s" could not be parsed, as %d is not a valid integer id' % (self._article['title'].encode('ascii', 'ignore'), self._article['id']))
            self._reset_article()

if __name__ == '__main__':
    reader = SampleReader('../data/training.xml', 4, 'tmp.json')
    reader.read()


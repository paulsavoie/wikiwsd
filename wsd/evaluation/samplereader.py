import logging
import random

class SampleReader:
    '''The SampleReader class reads a random number of samples from a wikipedia dump file and stores them
       in an output sample xml file to be used for the evaluation
    '''

    '''constructor

       @param path the path to the input wikipedia dump file
       @param num_samples the number of samples to be extracted
       @param output_path the path of the file to write the samples to
    '''
    def __init__(self, path, num_samples, output_path):
        self._path = path
        self._num_samples = num_samples
        self._output_path = output_path

    '''reads the samples and writes them to the specified output file
    '''
    def read(self):
        # read from actual file
        f = open(self._path, 'r')
        f.seek(0, 2) # go to the end of the file
        totalbytes = f.tell()
        max_end = round(float(f.tell())*0.8) # only go to 80% to make sure another sample follows

        out_xml = ('<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.8/" '
                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                   'xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.8/ '
                   'http://www.mediawiki.org/xml/export-0.8.xsd" version="0.8" xml:lang="en">\n')

        for sample in range(0, self._num_samples):
            # generate random number and go to file point
            start = random.randint(0, max_end)
            f.seek(start, 0)

            page_found = False
            page_done = False
            page_xml = ''
            while not page_found or not page_done:
                line = f.readline()
                if line.strip() == '<page>':
                    page_found = True
                elif line.strip() == '</page>' and page_found:
                    page_done = True
                elif line.strip()[0:9] == '<redirect':
                    page_found = False
                    page_xml = ''

                if page_found:
                    page_xml += line

            out_xml += page_xml

        f.close()
        # store samples in output file
        logging.info('Read %d samples from input file' % self._num_samples)

        out_xml += '</mediawiki>'

        output_f = open(self._output_path, 'w')
        output_f.write(out_xml)
        output_f.close()
        logging.info('Saved samples in output file %s' % (self._output_path))
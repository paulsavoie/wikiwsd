import unittest
import os
from wsd.evaluation.samplereader import SampleReader

class SampleReaderTest(unittest.TestCase):
    def setUp(self):
        self.output_path = 'wsd/tests/data/tmp.xmp'

    def tearDown(self):
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

    def test_sample(self):
        reader = SampleReader('wsd/tests/data/multiple1.xml', 1, self.output_path)
        reader.read()

        f = open(self.output_path)
        content = f.read()
        f.close()
        self.maxDiff = None
        expected = ('<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.8/" '
                    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                    'xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.8/ '
                    'http://www.mediawiki.org/xml/export-0.8.xsd" version="0.8" xml:lang="en">\n'
                    '  <page>\n'
                    '    <title>Dummy Title</title>\n'
                    '    <ns>0</ns>\n'
                    '    <id>123456</id>\n'
                    '    <revision>\n'
                    '      <id>530930715</id>\n'
                    '      <parentid>530791886</parentid>\n'
                    '      <timestamp>2013-01-02T15:40:49Z</timestamp>\n'
                    '      <contributor>\n'
                    '        <username>FigureArtist</username>\n'
                    '        <id>2148412</id>\n'
                    '      </contributor>\n'
                    '      <minor />\n'
                    '      <comment>/* Creative art and Fine art */ added hyperlink to creativity</comment>\n'
                    '      <text xml:space="preserve">This is a dummy text.</text>\n'
                    '      <sha1>9r03u34xpc7phjgxvp02n68wnsbemiw</sha1>\n'
                    '      <model>wikitext</model>\n'
                    '      <format>text/x-wiki</format>\n'
                    '    </revision>\n'
                    '  </page>\n'
                    '</mediawiki>')

        self.assertEqual(content, expected)



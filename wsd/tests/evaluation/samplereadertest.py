import unittest
import os
import json
from wsd.evaluation.samplereader import SampleReader

class SampleReaderTest(unittest.TestCase):
    def setUp(self):
        self.output_path = 'wsd/tests/data/temp.json'

    def tearDown(self):
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

    def test_sample(self):
        reader = SampleReader('wsd/tests/data/multiple.xml', 1, self.output_path)
        reader.read()

        f = open(self.output_path)
        content = f.read()
        f.close()
        self.maxDiff = None
        expected = [{
            'terms': [
                { 'index': 1, 'token': u'This', 'length': 1, 'isNoun': False },
                { 'index': 2, 'token': u'is', 'length': 1, 'isNoun': False },
                { 'index': 3, 'token': u'a', 'length': 1, 'isNoun': False },
                { 'index': 4, 'token': u'dummy', 'length': 1, 'isNoun': False },
                { 'index': 5, 'token': u'text.', 'length': 1, 'isNoun': False }
            ],
            'id': 123456,
            'links': {},
            'title': 'Dummy Title'
        }]
        self.assertEqual(content, json.JSONEncoder().encode(expected))



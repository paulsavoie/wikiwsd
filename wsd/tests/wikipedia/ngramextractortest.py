import unittest
import Queue
from wsd.wikipedia import NGramExtractor

class NGramExtractorTest(unittest.TestCase):

    def _process_text(self, text):
        extractor = NGramExtractor()
        article = {
            'id': 1,
            'type': 'article',
            'title': 'Dummy Title',
            'text': text
        }
        return extractor.process(article)

    def test_simple_text(self):
        text = 'This is a simple text.'
        self.assertEqual(self._process_text(text),
            [
                ('This', 0),
                ('is', 0),
                ('a', 0),
                ('simple', 0),
                ('text', 0),
                ('This is', 0),
                ('is a', 0),
                ('a simple', 0),
                ('simple text', 0),
                ('This is a', 0),
                ('is a simple', 0),
                ('a simple text', 0),
                ('This is a simple', 0),
                ('is a simple text', 0),
                ('This is a simple text', 0)
            ])

    def test_ngrams_multiple_lines(self):
        text = 'a line\nanother'
        self.assertEqual(self._process_text(text),
            [
                ('a', 0),
                ('line', 0),
                ('a line', 0),
                ('another', 0)
            ])

    def test_simple_link(self):
        text = 'Just [[a text]].'
        self.assertEqual(self._process_text(text),
            [
                ('Just', 0),
                ('a', 0),
                ('text', 0),
                ('Just a', 0),
                ('a text', 1),
                ('Just a text', 0)
            ])

    def test_different_target_link(self):
        text = 'Just [[target|a text]].'
        self.assertEqual(self._process_text(text),
            [
                ('Just', 0),
                ('a', 0),
                ('text', 0),
                ('Just a', 0),
                ('a text', 1),
                ('Just a text', 0)
            ])

    def test_tokens(self):
        text = 'Just, a text.'
        self.assertEqual(self._process_text(text),
            [
                ('Just', 0),
                ('a', 0),
                ('text', 0),
                ('Just, a', 0),
                ('a text', 0),
                ('Just, a text', 0)
            ])

    def test_phrases(self):
        text = 'Just; a text.'
        self.assertEqual(self._process_text(text),
            [
                ('Just', 0),
                ('a', 0),
                ('text', 0),
                ('a text', 0)
            ])

    def test_whole_link(self):
        text = '[[Just a text]]'
        self.assertEqual(self._process_text(text),
            [
                ('Just', 0),
                ('a', 0),
                ('text', 0),
                ('Just a', 0),
                ('a text', 0),
                ('Just a text', 1)
            ])

    def test_strip_ngrams(self):
        text = 'Just a text._ \n'
        self.assertEqual(self._process_text(text),
            [
                ('Just', 0),
                ('a', 0),
                ('text', 0),
                ('Just a', 0),
                ('a text', 0),
                ('Just a text', 0)
            ])

    def test_as_thread(self):
        input_queue = Queue.Queue()
        output_queue = Queue.Queue()
        extractor = NGramExtractor(input_queue, output_queue)
        extractor.start()
        article1 = {
            'id': 1,
            'type': 'article',
            'title': 'Article 1',
            'text': 'Just [[a text]].'
        }
        article2 = {
            'id': 2,
            'type': 'article',
            'title': 'Article 2',
            'text': 'And [[another]] one.'
        }
        input_queue.put(article1)
        input_queue.put(article2)
        input_queue.join()
        extractor.end()
        extractor.join()
        self.assertEqual(output_queue.empty(), False)
        ngrams1 = output_queue.get()
        self.assertEqual(ngrams1, 
            [
                ('Just', 0),
                ('a', 0),
                ('text', 0),
                ('Just a', 0),
                ('a text', 1),
                ('Just a text', 0)
            ])
        self.assertEqual(output_queue.empty(), False)
        ngrams2 = output_queue.get()
        self.assertEqual(ngrams2, [
                ('And', 0),
                ('another', 1),
                ('one', 0),
                ('And another', 0),
                ('another one', 0),
                ('And another one', 0)
            ])
import unittest
import Queue
from wsd.tests.database.databasemocks import *
from wsd.wikipedia import LinkExtractor

class LinkExtractorTest(unittest.TestCase):

    def setUp(self):
        self._work_view = WorkViewMock()

    def _process_text(self, text):
        article = {
            'id': 1,
            'title': 'Dummy Title',
            'text': text
        }
        extractor = LinkExtractor(self._work_view)
        extractor.process(article)
        return article

    def test_no_link(self):
        text = 'Text without link.'
        article = self._process_text(text)
        self.assertEqual(article['links'], [])
        self.assertEqual(article['text'], 'Text without link.\n')

    def test_single_link(self):
        self._work_view.articles['link'] = { 'id': 123, 'title': 'myArticle' }
        text = 'Text with single [[link]].'
        article = self._process_text(text)
        self.assertEqual(article['links'], [
                { 'target_article_id': 123, 'target_article_name': 'myArticle', 'phrase': 'link' }
            ])
        self.assertEqual(article['text'], 'Text with single [[link]].\n')

    def test_target(self):
        self._work_view.articles['link'] = { 'id': 123, 'title': 'myArticle' }
        text = 'Text with single [[link|text]].'
        article = self._process_text(text)
        self.assertEqual(article['links'], [
                { 'target_article_id': 123, 'target_article_name': 'myArticle', 'phrase': 'text' }
            ])
        self.assertEqual(article['text'], 'Text with single [[text]].\n')

    def test_multiple_links(self):
        self._work_view.articles['multiple'] = { 'id': 1, 'title': 'myArticle1' }
        self._work_view.articles['target'] = { 'id': 2, 'title': 'myArticle2' }
        text = 'Text with [[multiple]] [[target|links]] [[somewhere]].'
        article = self._process_text(text)
        self.assertEqual(article['links'], [
                { 'target_article_id': 1, 'target_article_name': 'myArticle1', 'phrase': 'multiple' },
                { 'target_article_id': 2, 'target_article_name': 'myArticle2', 'phrase': 'links' },
                { 'target_article_id': None, 'target_article_name': None, 'phrase': 'somewhere' }
            ])
        self.assertEqual(article['text'], 'Text with [[multiple]] [[links]] [[somewhere]].\n')

    def test_inner_links(self):
        # NOTE: inner links are neglected
        self._work_view.articles['target'] = { 'id': 100, 'title': 'Outer' }
        text = 'Text with [[target|an [[inner]] link]] and [[another one]].\n'
        article = self._process_text(text)
        self.assertEqual(article['links'], [
                { 'target_article_id': 100, 'target_article_name': 'Outer', 'phrase': 'an inner link'},
                { 'target_article_id': None, 'target_article_name': None, 'phrase': 'another one'}
            ])
        self.assertEqual(article['text'], 'Text with [[an inner link]] and [[another one]].\n')

    def test_multiple_lines(self):
        self._work_view.articles['multiple'] = { 'id': 1, 'title': 'myArticle1' }
        self._work_view.articles['target'] = { 'id': 2, 'title': 'myArticle2' }
        self._work_view.articles['line'] = { 'id': 3, 'title': 'myArticle3' }
        text = 'Text with [[multiple]] [[target|links]].\nAnd another [[line]] pointing somewhere.\n'
        article = self._process_text(text)
        self.assertEqual(article['links'], [
                { 'target_article_id': 1, 'target_article_name': 'myArticle1', 'phrase': 'multiple'},
                { 'target_article_id': 2, 'target_article_name': 'myArticle2', 'phrase': 'links'},
                { 'target_article_id': 3, 'target_article_name': 'myArticle3', 'phrase': 'line'}
            ])
        self.assertEqual(article['text'], 'Text with [[multiple]] [[links]].\nAnd another [[line]] pointing somewhere.\n')

    def test_as_thread(self):
        input_queue = Queue.Queue()
        output_queue = Queue.Queue()
        self._work_view.articles['multiple'] = { 'id': 1, 'title': 'myArticle1' }
        self._work_view.articles['target'] = { 'id': 2, 'title': 'myArticle2' }
        self._work_view.articles['line'] = { 'id': 3, 'title': 'myArticle3' }
        extractor = LinkExtractor(self._work_view, input_queue, output_queue)
        extractor.start()
        article1 = {
            'id': 100,
            'type': 'article',
            'title': 'Article 1',
            'text': 'Text with [[multiple]] [[target|links]].'
        }
        article2 = {
            'id': 200,
            'type': 'article',
            'title': 'Article 2',
            'text': 'And another [[line]] pointing somewhere.'
        }
        input_queue.put(article1)
        input_queue.put(article2)
        input_queue.join()
        extractor.end()
        extractor.join()
        self.assertEqual(output_queue.empty(), False)
        result1 = output_queue.get()
        self.assertEqual(result1['links'], [
                { 'target_article_id': 1, 'target_article_name': 'myArticle1', 'phrase': 'multiple'},
                { 'target_article_id': 2, 'target_article_name': 'myArticle2', 'phrase': 'links'}
            ])
        self.assertEqual(result1['text'], 'Text with [[multiple]] [[links]].\n')
        self.assertEqual(output_queue.empty(), False)
        result2 = output_queue.get()
        self.assertEqual(result2['links'], [
                { 'target_article_id': 3, 'target_article_name': 'myArticle3', 'phrase': 'line'}
            ])
        self.assertEqual(result2['text'], 'And another [[line]] pointing somewhere.\n')

    def test_real_1(self):
        text = ('thumb|right| Different C4-alkanes and -cycloalkanes (left to right): '
                    '[[n-butane|n-butane]] and [[isobutane]] are the two C4H10 isomers; [[cyclobutane]] and '
                    '[[methylcyclopropane]] are the two C4H8 isomers. Bicyclo[1.1.0]butane is the only '
                    'C4H6 compound and has no isomer; [[tetrahedrane]] (not shown) is the only C4H4 compound and has '
                    'also no isomer.\n')
        article = self._process_text(text)
        self.assertEqual(article['links'], [
                { 'target_article_id': None, 'target_article_name': None, 'phrase': 'n-butane'},
                { 'target_article_id': None, 'target_article_name': None, 'phrase': 'isobutane'},
                { 'target_article_id': None, 'target_article_name': None, 'phrase': 'cyclobutane'},
                { 'target_article_id': None, 'target_article_name': None, 'phrase': 'methylcyclopropane'},
                { 'target_article_id': None, 'target_article_name': None, 'phrase': 'tetrahedrane'}
            ])
        expected = ('thumb|right| Different C4-alkanes and -cycloalkanes (left to right): '
                    '[[n-butane]] and [[isobutane]] are the two C4H10 isomers; [[cyclobutane]] and '
                    '[[methylcyclopropane]] are the two C4H8 isomers. Bicyclo[1.1.0]butane is the only '
                    'C4H6 compound and has no isomer; [[tetrahedrane]] (not shown) is the only C4H4 compound and has '
                    'also no isomer.\n')
        self.assertEqual(article['text'], expected)

    def test_no_work_view(self):
        extractor = LinkExtractor(None)
        text = 'Text with [[multiple]] [[target|links]] [[somewhere]].'
        article = {
            'id': 1,
            'title': 'Dummy Title',
            'text': text
        }
        article = extractor.process(article)
        self.assertEqual(article['links'], [
                { 'target_article_id': None, 'target_article_name': 'multiple', 'phrase': 'multiple' },
                { 'target_article_id': None, 'target_article_name': 'target', 'phrase': 'links' },
                { 'target_article_id': None, 'target_article_name': 'somewhere', 'phrase': 'somewhere' }
            ])
        self.assertEqual(article['text'], 'Text with [[multiple]] [[links]] [[somewhere]].\n')
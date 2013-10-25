import unittest
import Queue
from wsd.wikipedia import WikipediaPreProcessor

class WikipediaPreProcessorTest(unittest.TestCase):

    def _process_text(self, text):
        processor = WikipediaPreProcessor()
        article = {
            'id': 1,
            'type': 'article',
            'title': 'Dummy Title',
            'text': text
        }
        processor.process(article)
        return article['text']

    def test_simple_text(self):
        processor = WikipediaPreProcessor()
        article = {
            'id': 1,
            'type': 'article',
            'title': 'Dummy Title',
            'text': 'This is a dummy text.'
        }
        result = processor.process(article)
        self.assertEqual(result, article)
        self.assertEqual(result['text'], 'This is a dummy text.\n')

    def test_hyphens(self):
        text = u'Just a text where someone says \'\'something\'\'\'.'
        self.assertEqual(self._process_text(text), u'Just a text where someone says something.\n')

    def test_single_line_comment(self):
        text = u'Just a text.<!-- with a comment -->\n<!-- and another comment -->and more text.'
        self.assertEqual(self._process_text(text), u'Just a text.\nand more text.\n')

    def test_multiple_line_comment(self):
        text = u'Just a text.<!-- with a comment\nthat goes over a line\n and another line -->\n<!-- and another comment -->and more text.'
        self.assertEqual(self._process_text(text), u'Just a text.\nand more text.\n')

    def test_html_tags_in_comment(self):
        text = u'Just a text.<!-- with a comment <div>with a <a href="here">tag</a>.</div> -->\n<!-- and another comment -->and more text.'
        self.assertEqual(self._process_text(text), u'Just a text.\nand more text.\n')

    def test_invalid_html_tags_in_comment(self):
        text = u'Just a text.<!-- with a comment <div>with a <a href="here">tag</a>. -->\n<!-- and another comment -->and more <div>abc</div>text.'
        self.assertEqual(self._process_text(text), u'Just a text.\nand more text.\n')

    def test_single_html_tag(self):
        # NOTE: text within tags is completely ignored
        text = u'Just a text<div class="abc">with a <a href="here>link</a> here</div>.'
        self.assertEqual(self._process_text(text), u'Just a text.\n')

    def test_html_tag_tree(self):
        text = u'Just a <div class="abc">with a <a href="here>link</a> here <br />which <p>spreads</p> over several <br /> lines</div>text.'
        self.assertEqual(self._process_text(text), u'Just a text.\n')

    def test_invalid_lines(self):
        text = u' | a wrong line\nJust a text.\n| and another wrong line\n! and another one\nand some proper text\n'
        self.assertEqual(self._process_text(text), u'Just a text.\nand some proper text\n')

    def test_incorrect_link(self):
        text = u'Just a text with an incorrect [[cat:abc|cat]].'
        self.assertEqual(self._process_text(text), u'Just a text with an incorrect cat.\n')

    def test_incorrect_link_followed(self):
        text = u'Just a text with an incorrect [[cat:abc|cat]] and a [[valid one]].'
        self.assertEqual(self._process_text(text), u'Just a text with an incorrect cat and a [[valid one]].\n')

    def test_links_in_link(self):
        # TODO: why is the second sentence stripped 
        text = u'Just a text with a weird [[outer|cat[[inner:incorrect]] link]].\nAnd another [[cat:else|interesting [[combination]]]]'
        self.assertEqual(self._process_text(text), u'Just a text with a weird [[outer|catinner:incorrect link]].\n')

    def test_pairs(self):
        text = u'Just a text with a [http://www.google.com] link.\n===title===\nand some more.'
        self.assertEqual(self._process_text(text), u'Just a text with a link.\nand some more.\n')

    def test_blocks(self):
        text = u'Just a text.\n{ and a block\n{ with another line\nand content again\n'
        self.assertEqual(self._process_text(text), u'Just a text.\nand content again\n')

    def test_empty_brackets(self):
        text = u'Just a link to google ([http://www.google.com]).'
        self.assertEqual(self._process_text(text), u'Just a link to google.\n')

    def test_html_whitespaces(self):
        text = u'Just  a&nbsp;text.'
        self.assertEqual(self._process_text(text), u'Just a text.\n')

    def test_strip_lines(self):
         text = u'*** Just a text.\r\n'
         self.assertEqual(self._process_text(text), u'Just a text.\n')

    def test_as_thread(self):
        input_queue = Queue.Queue()
        output_queue = Queue.Queue()
        processor = WikipediaPreProcessor(input_queue, output_queue)
        processor.start()
        article1 = {
            'id': 1,
            'type': 'article',
            'title': 'Article 1',
            'text': 'This is a text with a [[link|here] and an [[target:xy|invalid one]].'
        }
        article2 = {
            'id': 2,
            'type': 'article',
            'title': 'Article 2',
            'text': 'This is another text.\n===With a header===\n{ and a box\nWhich has an ending line.'
        }
        input_queue.put(article1)
        input_queue.put(article2)
        input_queue.join()
        processor.end()
        processor.join()
        self.assertEqual(output_queue.empty(), False)
        result1 = output_queue.get()
        self.assertEqual(result1['text'], 'This is a text with a [[link|here] and an invalid one.\n')
        self.assertEqual(output_queue.empty(), False)
        result2 = output_queue.get()
        self.assertEqual(result2['text'], 'This is another text.\nWhich has an ending line.\n')

    def test_real_1(self):
        # TODO: ??
        text = ('[[Image:Saturated C4 hydrocarbons ball-and-stick.png|thumb|right| '
                'Different C&lt;sub&gt;4&lt;/sub&gt;-alkanes and -cycloalkanes (left'
                ' to right): [[n-butane|''n''-butane]] and [[isobutane]] are the two '
                'C&lt;sub&gt;4&lt;/sub&gt;H&lt;sub&gt;10&lt;/sub&gt; isomers; [[cyclobutane]] ' 
                'and [[methylcyclopropane]] are the two C&lt;sub&gt;4&lt;/sub&gt;H&lt;sub&gt;8&lt;/sub&gt; '
                'isomers.&lt;br /&gt; Bicyclo[1.1.0]butane is the only '
                'C&lt;sub&gt;4&lt;/sub&gt;H&lt;sub&gt;6&lt;/sub&gt; compound and has no isomer; '
                '[[tetrahedrane]] (not shown) is the only C&lt;sub&gt;4&lt;/sub&gt;H&lt;sub&gt;4&lt;/sub&gt; ' 
                'compound and has also no isomer.]]')
        expected = ('')
        self.assertEqual(self._process_text(text), expected)

    def test_real_2(self):
        text = ('Perhaps the easiest way for U.S residents to envisage an acre is as a rectangle measuring 88 yards by 55 yards ({{frac|1'
                '|10}} of 880 yards by {{frac|1|16}} of 880 yards), about {{frac|9|10}} the size of a standard [[American football field]'
                ']. [[File:Acre over US and Associationl football field.svg|frame|The area of one acre (red) superposed on an [[American'
                'football]] field (green) and [[association football]] (soccer) pitch (blue).]] To be more exact, one acre is 90.75 perce'
                'nt of a {{convert|100|yd|m|2|abbr=off|lk=in}} long by {{convert|53.33|yd|m|abbr=off|lk=in}} wide American football field'
                ' (without the [[end zone]]s). The full field, including the end zones, covers approximately {{convert|1.32|acres|2|abbr='
                'on}}.')
        expected =  ('Perhaps the easiest way for U.S residents to envisage an acre is as a rectangle measuring 88 yards by 55 yards ('
                ' of 880 yards by of 880 yards), about the size of a standard [[American football field]'
                ']. frame|The area of one acre (red) superposed on an [[American'
                'football]] field (green) and [[association football]] (soccer) pitch (blue). To be more exact, one acre is 90.75 perce'
                'nt of a long by wide American football field'
                ' (without the [[end zone]]s). The full field, including the end zones, covers approximately.\n')
        self.assertEqual(self._process_text(text), expected)
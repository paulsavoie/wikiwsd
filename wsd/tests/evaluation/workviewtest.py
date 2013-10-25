import unittest
from wsd.tests.database.databasemocks import *
from wsd.evaluation.workview import EvaluationWorkView

class EvaluationWorkViewTest(unittest.TestCase):
    def setUp(self):
        self.mock = WorkViewMock()
        sample = {
            'title': 'my sample',
            'id': 1,
            'links': [
                { 'target_article_name': 'myLink1', 'target_article_id': 5, 'phrase': 'p1' },
                { 'target_article_name': 'myLink2', 'target_article_id': 6, 'phrase': 'p2' },
                { 'target_article_name': 'myLink1', 'target_article_id': 5, 'phrase': 'p3' },
            ],
            'ngrams': [ # only required for occurrences
                ('my ngram 1', 0),
                ('my ngram 2', 1),
                ('my ngram 2', 0)
            ]
        }
        self.work_view = EvaluationWorkView(self.mock, sample)

    def test_article_by_title_own_link(self):
        self.mock.articles['my sample'] = { 'id': 1 }
        self.assertEqual(self.work_view.resolve_title('my sample'), None)

    def test_article_by_title_non_existent(self):
        self.assertEqual(self.work_view.resolve_title('non existent'), None)

    def test_article_by_title(self):
        article = { 'id': 3, 'title': 'new article', 'articleincount': 55 }
        self.mock.articles['new article'] = article
        self.assertEqual(self.work_view.resolve_title('new article'), article)

    def test_number_of_common(self):
        self.mock.commons.append({ 'id1': 5, 'id2': 6, 'num': 10 })
        self.mock.commons.append({ 'id1': 5, 'id2': 7, 'num': 10 })
        self.assertEqual(self.work_view.retrieve_number_of_common_articles(5, 6), 9)
        self.assertEqual(self.work_view.retrieve_number_of_common_articles(5, 7), 10)

    def test_number_of_common_invalid(self):
        self.assertEqual(self.work_view.retrieve_number_of_common_articles(5, 6), 0)

    def test_meanings(self):
        self.mock.meanings['term1'] = [
            { 'id': 5, 'title': 'myLink1', 'articleincount': 2, 'occurrences': 3 },
            { 'id': 6, 'title': 'myLink2', 'articleincount': 2, 'occurrences': 3 },
            { 'id': 7, 'title': 'myLink3', 'articleincount': 2, 'occurrences': 3 }
        ]
        meanings = self.work_view.retrieve_meanings('term1')
        self.assertEqual(len(meanings), 3)
        self.assertEqual(meanings[0]['articleincount'], 1)
        self.assertEqual(meanings[0]['occurrences'], 1)
        self.assertEqual(meanings[1]['articleincount'], 1)
        self.assertEqual(meanings[1]['occurrences'], 2)
        self.assertEqual(meanings[2]['articleincount'], 2)
        self.assertEqual(meanings[2]['occurrences'], 3)

    def test_meanings_remove(self):
        self.mock.meanings['term1'] = [
            { 'id': 5, 'title': 'myLink1', 'articleincount': 2, 'occurrences': 2 },
            { 'id': 6, 'title': 'myLink2', 'articleincount': 1, 'occurrences': 3 }
        ]
        meanings = self.work_view.retrieve_meanings('term1')
        self.assertEqual(len(meanings), 0)

    def test_occurrences(self):
        self.mock.occurrences['my ngram 1'] = { 'occurrences': 3, 'as_link': 0 }
        self.mock.occurrences['my ngram 2'] = { 'occurrences': 4, 'as_link': 3 }
        self.mock.occurrences['my ngram 3'] = { 'occurrences': 3, 'as_link': 1 }

        occurrences1 = self.work_view.retrieve_occurrences('my ngram 1')
        occurrences2 = self.work_view.retrieve_occurrences('my ngram 2')
        occurrences3 = self.work_view.retrieve_occurrences('my ngram 3')

        self.assertEqual(occurrences1['occurrences'], 2)
        self.assertEqual(occurrences2['occurrences'], 2)
        self.assertEqual(occurrences3['occurrences'], 3)
        self.assertEqual(occurrences1['as_link'], 0)
        self.assertEqual(occurrences2['as_link'], 2)
        self.assertEqual(occurrences3['as_link'], 1)
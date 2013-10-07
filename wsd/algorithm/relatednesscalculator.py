import math
from wsd.algorithm import RelatednessRetriever

TOTAL_ARTICLES = 4696033.0 # TOOD: define somewhere else?

class RelatednessCalculator:
    '''calculator to get the relatedness between to meanings
    '''

    '''constructor

        @param work_view the work view to connect to the database
    '''
    def __init__(self, work_view):
        self._relatedness_retriever = RelatednessRetriever(work_view)

    '''calculates the relatedness

        @param m1 --- link 1 as dictionary with fields 'target_article_id' and 'articleincount'
        @param m2 --- link 2 as dictionary with fields 'target_article_id' and 'articleincount'

        @return a relatedness measure that defines how close the two articles relate
    '''
    def calculate_relatedness(self, m1, m2):

        a_total_in = float(m1['articleincount'])
        b_total_in = float(m2['articleincount'])

        if round(a_total_in) == 0 or round(b_total_in) == 0:
            return 0.0

        common_in = float(self._relatedness_retriever.retrieve_relatedness(m1, m2))

        if common_in == 0.0:
            return 0.0

        relatedness = (math.log(max(a_total_in, b_total_in)) - math.log(common_in)) / (math.log(TOTAL_ARTICLES) - math.log(min(a_total_in, b_total_in)))
        return relatedness
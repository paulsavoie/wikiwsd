# -*- coding: utf-8 -*-
'''
This file contains the algorithm to calculate the
relatedness between two articles

Author: Paul Laufer
Date: Jun 2013

'''

import math

class RelatednessCalculator:
    '''calculator to get the relatedness between to meanings
    '''

    '''constructor

    Arguments:
        commonness_retriever --- a CommonnessRetriever instance
    '''
    def __init__(self, commonness_retriever):
        self.__commonness_retriever = commonness_retriever

    '''calculates the relatedness using the commonness retriever instance

    Arguments:
        m1 --- article 1 as dictionary with fields 'id' and 'articleincount'
        m2 --- article 2 as dictionary with fields 'id' and 'articleincount'
    '''
    def calculate_relatedness(self, m1, m2):

        a_total_in = float(m1['articleincount'])
        b_total_in = float(m2['articleincount'])

        if round(a_total_in) == 0 or round(b_total_in) == 0:
            return 0.0

        common_in = self.__commonness_retriever.retrieve_commonness(m1, m2)
        total_articles = 4696033.0

        if common_in == 0.0:
            return 0.0

        #return common_in / (a_total_in + b_total_in) # does not work so vell in general (if stddev < 3, take other measure)

        relatedness = (math.log(max(a_total_in, b_total_in)) - math.log(common_in)) / (math.log(total_articles) - math.log(min(a_total_in, b_total_in)))
        return relatedness
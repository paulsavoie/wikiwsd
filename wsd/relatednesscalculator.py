import math

class RelatednessCalculator:
    def __init__(self, commonness_retriever):
        self.__commonness_retriever = commonness_retriever

    def calculate_relatedness(self, m1, m2):

        a_total_in = float(m1['articleincount'])
        b_total_in = float(m2['articleincount'])

        if a_total_in == 0.0 or b_total_in == 0.0:
            return 0.0

        common_in = self.__commonness_retriever.retrieve_commonness(m1, m2)
        total_articles = 4696033.0

        if common_in == 0.0:
            return 0.0

        #return common_in / (a_total_in + b_total_in) # does not work so vell in general (if stddev < 3, take other measure)

        relatedness = (math.log(max(a_total_in, b_total_in)) - math.log(common_in)) / (math.log(total_articles) - math.log(min(a_total_in, b_total_in)))
        return relatedness
# -*- coding: utf-8 -*-
'''
This file contains the algorithm which selects the
best meaning for each term to be disambiguated

Author: Paul Laufer
Date: Jun 2013

'''

import logging

class Decider:
    '''class to decide for a specific term
    '''

    '''constructor

    Arguments:
        relatedness_calculator --- instance of RelatednessCalculator 
    '''
    def __init__(self, relatedness_calculator):
        self._relatedness_calculator = relatedness_calculator

    '''decides for a meaning for each word to be disambiguated
       the resultant index of the best disambiguation will be stored in the field
       'finalIndex' of each term (default to -1 if no disambiguation possible)

    Arguments:
        words --- a list of dictionaries with the following fields:
            - isNoun --- boolean whether the word shall be disambiguated
            - token --- the actual terms of the words
            - disambiguations --- a list of dictionaries holding the possible meanings with fields
                - meaning --- the textual representation of the meaning
                - id --- the id of the wikipedia article it references
                - articleincount --- the number of articles that link to the meaning
    '''
    def decide(self, words):
        # extract nouns
        nouns = []
        index = 0
        for word in words:
            if word['isNoun']:
                word['numCmp'] = 0
                word['finalIndex'] = -1
                word['done'] = False
                word['termIndex'] = index
                for disambiguation in word['disambiguations']:
                    disambiguation['cumulativeRelatedness'] = 0.0
                    disambiguation['overallMatch'] = 0.0
                    disambiguation['averageRelatedness'] = 0.0
                index += 1
                nouns.append(word)

        num_finalized = 0
        while (num_finalized != len(nouns)):
            next_noun_index = self._find_next_noun_index(nouns)
            logging.info('%d of %d words disambiguated | %d%% DONE' % (num_finalized, len(nouns), float(num_finalized) / float(len(nouns)) * 100.0))
            if next_noun_index == -1:
                logging.error('No next noun was found!')
            else:
                if len(nouns[next_noun_index]['disambiguations']) == 1: # if only one meaning, take it
                    nouns[next_noun_index]['finalIndex'] = 0
                    num_finalized += 1
                    logging.info('Only meaning for %s was selected: %s' % (nouns[next_noun_index]['token'], nouns[next_noun_index]['disambiguations'][0]['meaning']))
                elif len(nouns[next_noun_index]['disambiguations']) == 0: # just continue
                    logging.error('noun %s does not have any disambiguations' % nouns[next_noun_index]['token'])
                    num_finalized += 1
                else:
                    start = next_noun_index-3
                    end = next_noun_index+3 # TODO: should be +4 (end is not included)
                    if end > len(nouns):
                        end = len(nouns)
                        start = end - 7
                    if start < 0:
                        start = 0
                        end = start + 7
                        if end > len(nouns):
                            end = len(nouns)

                    for index in range(start, end):
                        if index != next_noun_index: # do not compare to itself
                            logging.info('comparing %s to %s' % (nouns[next_noun_index]['token'], nouns[index]['token']))
                            if nouns[index]['finalIndex'] != -1:
                                neighbour_disambiguations = [nouns[index]['disambiguations'][nouns[index]['finalIndex']]]
                            else:
                                neighbour_disambiguations = nouns[index]['disambiguations']
                            for neighbour_disambiguation in neighbour_disambiguations:
                                # compare every disambiguation to every other one
   
                                for disambiguation in nouns[next_noun_index]['disambiguations']:
                                    relatedness = self._relatedness_calculator.calculate_relatedness(disambiguation, neighbour_disambiguation)

                                    #if len(neighbour_disambiguations) == 1: 
                                    #    relatedness *= 2.0
                                    disambiguation['cumulativeRelatedness'] += (relatedness / float(len(neighbour_disambiguations))) # if only one, it counts more
                            # normalize relatedness
                            #total_relatedness = 0.0
                            #for disambiguation in nouns[next_noun_index]['disambiguations']:
                            #    total_relatedness += disambiguation['cumulativeRelatedness']

                            #for disambiguation in nouns[next_noun_index]['disambiguations']:
                            #    if total_relatedness == 0.0:
                            #        normalizedCumulative = 0.0
                            #    else:
                            #        normalizedCumulative = disambiguation['cumulativeRelatedness'] / total_relatedness
                            #    disambiguation['averageRelatedness'] = normalizedCumulative
                            #    disambiguation['overallMatch'] = normalizedCumulative * disambiguation['percentage']

                            nouns[next_noun_index]['numCmp'] += 1 # noun compared to one more neighbour

                            # JUST FOR DEBUGGING REASONS
                            disambiguations_tmp = list(nouns[next_noun_index]['disambiguations'])
                            sorted_tmp = sorted(disambiguations_tmp, key=lambda dis: -dis['cumulativeRelatedness'])
                            logging.info('\tcumulative (%f): %s' % (sorted_tmp[0]['cumulativeRelatedness'], sorted_tmp[0]['meaning'].encode('ascii', 'ignore')))
                            if len(sorted_tmp) > 1:
                                logging.info('\tcumulative 2nd (%f): %s' % (sorted_tmp[1]['cumulativeRelatedness'], sorted_tmp[1]['meaning'].encode('ascii', 'ignore')))

                    numCmp = nouns[next_noun_index]['numCmp']
                    if numCmp != 0:
                        # normalize relatedness
                        total_relatedness = 0.0
                        for disambiguation in nouns[next_noun_index]['disambiguations']:
                            total_relatedness += disambiguation['cumulativeRelatedness']

                        if total_relatedness != 0.0:
                            for disambiguation in nouns[next_noun_index]['disambiguations']:
                                disambiguation['averageRelatedness'] = disambiguation['cumulativeRelatedness'] / total_relatedness #float(numCmp)
                                disambiguation['overallMatch'] = (disambiguation['averageRelatedness'] + disambiguation['percentage']) / 2.0 # take average


                    # take the best match
                    sorted_disambiguations = sorted(nouns[next_noun_index]['disambiguations'], key=lambda dis: -dis['overallMatch'])
                    tmp_index = 0
                    while (nouns[next_noun_index]['finalIndex'] == -1):
                        if  nouns[next_noun_index]['disambiguations'][tmp_index]['id'] == sorted_disambiguations[0]['id']:
                            nouns[next_noun_index]['finalIndex'] = tmp_index 
                            num_finalized += 1 
                            logging.info('deciding for %s, rel: %d%%, comm: %d%%, total: %d%%' % (sorted_disambiguations[0]['meaning'], round(sorted_disambiguations[0]['averageRelatedness']*100), round(sorted_disambiguations[0]['percentage']*100), round(sorted_disambiguations[0]['overallMatch']*100)))
                        tmp_index = tmp_index + 1
                    if len(sorted_disambiguations) > 1:
                        logging.info('2nd choice would be %s, rel: %d%%, comm: %d%%, total: %d%%' % (sorted_disambiguations[1]['meaning'], round(sorted_disambiguations[1]['averageRelatedness']*100), round(sorted_disambiguations[1]['percentage']*100), round(sorted_disambiguations[1]['overallMatch']*100)))

        return

        # order nouns by cardinality asc
        sorted_nouns = sorted(nouns, key=lambda noun: len(noun['disambiguations']))

        # start with lowest cardinality and decide
        for index in range(0, len(nouns)):
            noun = sorted_nouns[index]
            if noun['finalIndex'] == -1 and len(noun['disambiguations']) > 0: # only if not decided yet

                # if there is only one possible meaning, take it
                if len(noun['disambiguations']) == 1:
                    noun['finalIndex'] = 0
                else:

                    # compare to all others in surrounding (min 6)
                    start_2 = noun['termIndex'] - 3
                    if start_2 < 0:
                        start_2 = 0
                    end_2 = start_2 + 7
                    if end_2 > len(nouns):
                        end_2 = len(nouns)
                        start_2 = end_2-7
                        if start_2 < 0:
                            start_2 = 0
                    for index2 in range(start_2, end_2):
                        if noun['token'] != nouns[index2]['token'] and noun['finalIndex'] == -1:
                            noun2 = nouns[index2]
                            logging.info('comparing %s to %s' % (noun['token'], noun2['token']))
                            if noun2['finalIndex'] != -1:
                                noun2_disambiguations = [noun2['disambiguations'][noun2['finalIndex']]]
                            else:
                                noun2_disambiguations = noun2['disambiguations']
                            for disambiguation2 in noun2_disambiguations:
                                # compare every disambiguation to every other one
                                for disambiguation in noun['disambiguations']:
                                    #print 'retrieving relatedness between %s and %s' % (disambiguation['meaning'].encode('ascii', 'ignore'), disambiguation2['meaning'].encode('ascii', 'ignore'))
                                    relatedness = self._relatedness_calculator.calculate_relatedness(disambiguation, disambiguation2)
                                    #print '\t: relatedness of %s to %s: %f' % (disambiguation['meaning'].encode('ascii', 'ignore'), disambiguation2['meaning'].encode('ascii', 'ignore'), relatedness)
                                    
                                    disambiguation['cumulativeRelatedness'] += (relatedness / float(len(noun2_disambiguations))) # if only one, it counts more

                                # normalize relatedness
                                total_relatedness = 0.0
                                for disambiguation in noun['disambiguations']:
                                    total_relatedness += disambiguation['cumulativeRelatedness']

                                for disambiguation in noun['disambiguations']:
                                    if total_relatedness == 0.0:
                                        normalizedCumulative = 0.0
                                    else:
                                        normalizedCumulative = disambiguation['cumulativeRelatedness'] / total_relatedness
                                    disambiguation['averageRelatedness'] = normalizedCumulative
                                    disambiguation['overallMatch'] = normalizedCumulative * disambiguation['percentage']

                            noun['numCmp'] += 1 # noun compared to one more
                            
                            # sort disambiguations according to cumulative relatedness
                            disambiguations_copy = list(noun['disambiguations'])
                            sorted_disambiguations = sorted(disambiguations_copy, key=lambda dis: -dis['overallMatch'])

                            disambiguations_tmp = list(noun['disambiguations'])
                            sorted_tmp = sorted(disambiguations_tmp, key=lambda dis: -dis['averageRelatedness'])
                            logging.info('\tbest match (%f): %s' % (sorted_tmp[0]['averageRelatedness'], sorted_tmp[0]['meaning'].encode('ascii', 'ignore')))

                            # if compared to at least 4 other nouns and cumulativeRelatedness of first is significantly higher than of second, take first
                            if noun['numCmp'] > 3 and sorted_disambiguations[0]['overallMatch'] > 2.5 * sorted_disambiguations[1]['overallMatch']:
                                # find original index
                                tmp_index = 0
                                while (noun['finalIndex'] == -1):
                                    if  noun['disambiguations'][tmp_index]['id'] == sorted_disambiguations[0]['id']:
                                        noun['finalIndex'] = tmp_index 
                                    tmp_index = tmp_index + 1
                    
                    # take the best match
                    disambiguations_copy = list(noun['disambiguations'])
                    sorted_disambiguations = sorted(disambiguations_copy, key=lambda dis: -dis['overallMatch'])
                    tmp_index = 0
                    while (noun['finalIndex'] == -1):
                        if  noun['disambiguations'][tmp_index]['id'] == sorted_disambiguations[0]['id']:
                            noun['finalIndex'] = tmp_index
                        tmp_index = tmp_index + 1

    def _find_next_noun_index(self, nouns):
        lowest_cardinality = 99999
        next_noun_index = -1
        # find noun which is already determined
        index = 0
        for index in range(0, len(nouns)):
            if nouns[index]['done'] == False:
                # find neighbours to this noun
                start = index-3
                end = index+3
                if start < 0:
                    start = 0
                if end >= len(nouns):
                    end = len(nouns)-1
                for neighbour_index in range(start, end+1):
                    if nouns[neighbour_index]['done'] == False and len(nouns[neighbour_index]['disambiguations']) < lowest_cardinality:
                        next_noun_index = neighbour_index
                        lowest_cardinality = len(nouns[neighbour_index]['disambiguations'])

        # if none was found take one with lowest cardinality that wasn't selected yet
        if next_noun_index == -1:
            for index in range(0, len(nouns)):
                if nouns[index]['done'] == False and len(nouns[index]['disambiguations']) < lowest_cardinality:
                    next_noun_index = index
                    lowest_cardinality = len(nouns[index]['disambiguations'])

        # mark as done
        nouns[next_noun_index]['done'] = True
        return next_noun_index
import logging

CONSIDER_NEIGHBORING_NODES_AS_CONTEXT = 6 # defines the number of links the surrounding to consider as neighbouring nodes

class Decider:
    '''The Decider class takes the several metrics into account and
       identifies a meaning for each link that is most likely to be the correct one in the 
       given context
    '''

    '''constructor

       @param relatedness_calculator a relatedness calculator to improve the decision making process
    '''
    def __init__(self, relatedness_calculator):
        self._relatedness_calculator = relatedness_calculator

    '''decides for a meaning for each word to be disambiguated. The meanings will be sorted with the most likely one 
       as the first entry in the list of meanings for each link in article['links'].
       additionally, a 'relatedness' field is added that determines how relevant the field is
       finally, a combined value of 'commonness' and 'relatedness' is calculated which is added as an 'overallMatch' field

       @param article an article as a dictionary with the following fields:
              'id': the id of the article
              'links': a list of links to be disambiguated as dictionaries with the following fields:
                  'phrase': the phrase used within the link
                  'meanings' a list of of dictionaries with the following fields:
                      'target_article_id': the id of the referenced article
                      'target_article_name': the name of the referenced article
                      'commonness': a value between 0 and 1 that determines how popular this meaning is
                      'articleincount': a number how many times this article is linked to
    '''
    def decide(self, article):
        links = article['links']
        # create fields
        for link in links:
            link['done'] = False # will be deleted later, only for temporary usage
            link['numCmp'] = 0 # will be deleted later, only for temporary usage
            for m in link['meanings']:
                m['relatedness'] = 0.0
                m['overallMatch'] = 0.0
                m['cumulativeRelatedness'] = 0.0 # will be deleted later, only for temporary usage


        num_finalized = 0
        while (num_finalized != len(links)):
            next_link_index = self._find_next_link_index(links)
            logging.info('%d of %d words disambiguated | %d%% DONE' % (num_finalized, len(links), float(num_finalized) / float(len(links)) * 100.0))
            if next_link_index == -1:
                logging.error('No next link was found!')
                num_finalized+= 1
            else:
                # if only meaning, take it
                link = links[next_link_index]
                if len(link['meanings']) == 1:
                    logging.info('Only meaning for %s was selected: %s' % (link['phrase'], link['meanings'][0]['target_article_name']))
                # if there is no meaning, just continue
                elif len(link['meanings']) == 0:
                    logging.error('link %s does not have any disambiguations' % link['phrase'])
                # if multiple meanings are available
                else:
                    start = next_link_index-(CONSIDER_NEIGHBORING_NODES_AS_CONTEXT/2)
                    if start < 0:
                        start = 0
                    end = start + CONSIDER_NEIGHBORING_NODES_AS_CONTEXT
                    if end >= len(links):
                        end = len(links) - 1
                    for index in range(start, end+1):
                        # correlation with link itself is not useful ;-)
                        if index != next_link_index:
                            logging.info('comparing %s to %s' % (link['phrase'], links[index]['phrase']))
                            # if there is already a meaning selected for the compared link
                            if links[index]['done']:
                                if len(links[index]['meanings']) == 0:
                                    neighbour_meanings = []
                                else:
                                    neighbour_meanings = [links[index]['meanings'][0]]
                            else:
                                neighbour_meanings = links[index]['meanings']
                            # compare each neighboring meaning to the current one
                            for neighbour_meaning in neighbour_meanings:
                                for meaning in link['meanings']:
                                    relatedness = self._relatedness_calculator.calculate_relatedness(meaning, neighbour_meaning)
                                    # add to cumulative relatedness
                                    meaning['cumulativeRelatedness'] += (relatedness / float(len(neighbour_meanings)))

                            # mark link as compared to one more link
                            link['numCmp'] += 1

                            # JUST FOR DEBUGGING REASONS
                            meanings_tmp = list(link['meanings'])
                            sorted_tmp = sorted(meanings_tmp, key=lambda m: -m['cumulativeRelatedness'])
                            logging.info('\tcumulative (%f): %s' % (sorted_tmp[0]['cumulativeRelatedness'], sorted_tmp[0]['target_article_name']))
                            if len(sorted_tmp) > 1:
                                logging.info('\tcumulative 2nd (%f): %s' % (sorted_tmp[1]['cumulativeRelatedness'], sorted_tmp[1]['target_article_name']))
                    # calculate relatedness and overall match
                    total_relatedness = 0.0
                    for meaning in link['meanings']:
                        total_relatedness += meaning['cumulativeRelatedness']

                    for meaning in link['meanings']:
                        if total_relatedness != 0.0:
                            meaning['relatedness'] = meaning['cumulativeRelatedness'] / total_relatedness
                        meaning['overallMatch'] = (meaning['relatedness'] + meaning['commonness']) / 2.0

                    # take the best match
                    link['meanings'] = sorted(link['meanings'], key=lambda m: -m['overallMatch'])
                    logging.info('deciding for %s, rel: %d%%, comm: %d%%, total: %d%%' 
                                % (link['meanings'][0]['target_article_name'], 
                                   round(link['meanings'][0]['relatedness']*100.0),
                                   round(link['meanings'][0]['commonness']*100.0),
                                   round(link['meanings'][0]['overallMatch']*100.0)))
                    if len(link['meanings']) > 1:
                        logging.info('2nd choice would be %s, rel: %d%%, comm: %d%%, total: %d%%'
                            % (link['meanings'][1]['target_article_name'], 
                                   round(link['meanings'][1]['relatedness']*100.0),
                                   round(link['meanings'][1]['commonness']*100.0),
                                   round(link['meanings'][1]['overallMatch']*100.0)))

                link['done'] = True
                num_finalized += 1

        # cleanup and delete unccessecary fields
        for link in links:
            del link['done']
            del link['numCmp']
            for m in link['meanings']:
                if m.has_key('cumulativeRelatedness'): # TODO: investigate why this field is missing sometimes
                    del m['cumulativeRelatedness']

    def _find_next_link_index(self, links):
        # it there is one with only one meaning left, take that one first
        for index in range(0, len(links)):
            if len(links[index]['meanings']) == 1 and links[index]['done'] == False:
                return index

        # otherwise take one with the most number of neighbouring nodes that are already determined and the lowest cardinality next
        lowest_cardinality = 99999
        highest_neighbours_done = 0
        next_link_index = -1
        # find a link which is already determined
        for index in range(0, len(links)):
            if links[index]['done'] == False:
                # find neighbours to this link
                start = index-(CONSIDER_NEIGHBORING_NODES_AS_CONTEXT/2)
                if start < 0:
                    start = 0
                end = start + CONSIDER_NEIGHBORING_NODES_AS_CONTEXT
                if end >= len(links):
                    end = len(links) - 1

                neighbours_done = 0
                for neighbour_index in range(start, end+1):
                    if links[neighbour_index]['done']:
                        neighbours_done+= 1

                if (neighbours_done == highest_neighbours_done and len(links[index]['meanings']) < lowest_cardinality) or neighbours_done > highest_neighbours_done:
                    next_link_index = index
                    highest_neighbours_done = neighbours_done
                    lowest_cardinality = len(links[index]['meanings'])

        return next_link_index
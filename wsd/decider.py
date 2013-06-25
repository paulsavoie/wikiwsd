class Decider:
    def __init__(self, relatedness_calculator):
        self.__relatedness_calculator = relatedness_calculator

    def decide(self, words):
        # extract nouns
        nouns = []
        for word in words:
            if word['isNoun']:
                word['numCmp'] = 0
                word['finalIndex'] = -1
                nouns.append(word)

        # order nouns by cardinality asc
        #sorted_nouns = sorted(nouns, key=lambda noun: len(noun['disambiguations']))

        # temporary cache for relatedness
        relatedness_cache = {}
        # quickly fill cache to make life easier
        for noun in nouns:
            for disambiguation in noun['disambiguations']:
                relatedness_cache[disambiguation['id']] = { }

        # start with lowest cardinality and decide
        for index in range(0, len(nouns)):
            noun = nouns[index]
            if noun['finalIndex'] == -1 and len(noun['disambiguations']) > 0: # only if not decided yet

                # if there is only one possible meaning, take it
                if len(noun['disambiguations']) == 1:
                    noun['finalIndex'] = 0
                else:

                    # compare to all others in surrounding (min 6)
                    start_2 = index - 3
                    if start_2 < 0:
                        start_2 = 0
                    end_2 = start_2 + 7
                    if end_2 > len(nouns):
                        end_2 = len(nouns)
                        start_2 = end_2-7
                        if start_2 < 0:
                            start_2 = 0
                    for index2 in range(start_2, end_2):
                        if index2 != index and noun['finalIndex'] == -1:
                            noun2 = nouns[index2]
                            print 'comparing %s to %s' % (noun['token'], noun2['token'])
                            if noun2['finalIndex'] != -1:
                                noun2_disambiguations = [noun2['disambiguations'][noun2['finalIndex']]]
                            else:
                                noun2_disambiguations = noun2['disambiguations']
                            for disambiguation2 in noun2_disambiguations:
                                # compare every disambiguation to every other one
                                for disambiguation in noun['disambiguations']:
                                    # first, lookup in cache
                                    if relatedness_cache[disambiguation['id']].has_key(disambiguation2['id']):
                                        relatedness = relatedness_cache[disambiguation['id']][disambiguation2['id']]
                                    else: # otherwise calculate
                                        #print 'retrieving relatedness between %s and %s' % (disambiguation['meaning'].encode('ascii', 'ignore'), disambiguation2['meaning'].encode('ascii', 'ignore'))
                                        relatedness = self.__relatedness_calculator.calculate_relatedness(disambiguation, disambiguation2)
                                        #print '\t: relatedness of %s to %s: %f' % (disambiguation['meaning'].encode('ascii', 'ignore'), disambiguation2['meaning'].encode('ascii', 'ignore'), relatedness)
                                        # store for later in cache
                                        relatedness_cache[disambiguation['id']][disambiguation2['id']] = relatedness
                                        relatedness_cache[disambiguation2['id']][disambiguation['id']] = relatedness
                                    
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
                            print '\tbest match (%f): %s' % (sorted_tmp[0]['averageRelatedness'], sorted_tmp[0]['meaning'].encode('ascii', 'ignore'))

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
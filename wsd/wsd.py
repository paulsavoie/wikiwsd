"""The main program
"""

import time
import MySQLdb as mysqldb
import nltk
import math
from outputter import HTMLOutputter

class WordSenseDisambiguator():
    def __init__(self, input_file='../data/simpleinput.txt', output_file='../data/simpleoutput.html',
            db_host='localhost', db_user='wikiwsd', db_pass='wikiwsd'):
        self._db_connection = mysqldb.connect(db_host, db_user, db_pass, 'wikiwsd3', charset='utf8', use_unicode=True)
        self._input_file = input_file
        self._output_file = output_file

    def __retrieve_words(self):
        # read text from input file
        f = open(self._input_file, 'r')
        text = f.read()
        f.close()

        # process text to tokenize and pos-tag it
        tokenized = nltk.wordpunct_tokenize(text)
        tagged = nltk.pos_tag(tokenized)

        # extract words
        words = []
        index = 0
        prevNoun = False
        for token in tagged:
            word = token[0]
            tag = token[1]
            if tag[0:2] == 'NN':
                # combine adjacent nouns
                if prevNoun:
                    words[len(words)-1]['token'] = words[len(words)-1]['token'] + ' %s' % (word)
                    words[len(words)-1]['length'] += 1
                else:
                    words.append({'token': word, 'isNoun': True, 'tag': tag, 'index': index, 'length': 1, 'disambiguations': []})
                prevNoun = True
            else:
                words.append({'token': word, 'isNoun': False, 'tag': tag, 'index': index, 'length': 1})
                prevNoun = False
            index+= 1

        return words

    def __retrieve_disambiguations(self, words):
        cur = self._db_connection.cursor()
        disambiguations = {}

        # retrieve disambiguations ordered by frequency        
        for word in words:
            if word['isNoun']:
                if disambiguations.has_key(word['token']):
                    word['disambiguations'] = disambiguations[word['token']] 
                else: # only if not retrieved yet
                    print 'retrieving disambiguations for %s' % (word['token'])
                    #noun_disambiguations = []

                    # check if an article exists with the title of the noun and add as 100%
                    
                    #cur.execute('SELECT COUNT(*) FROM articles WHERE title=%s;', noun['token'])
                    #result = cur.fetchone()
                    #if result[0] > 0:
                    #    noun_disambiguations.append({'percentage': 1.0, 'meaning': noun['token']})

                    # select disambiguations
                    #cur.execute('SELECT COUNT(*) AS `occurrences`, `string`, `meaning` FROM `disambiguations` WHERE `string` = %s GROUP BY `string`, `meaning` ORDER BY `occurrences` DESC;', 
                    #    word['token'])
                    cur.execute('SELECT target_article_id, articles.title, SUM(occurrences) as occurrences, articles.articleincount FROM disambiguations LEFT JOIN articles ON articles.id = disambiguations.target_article_id WHERE string = %s GROUP BY target_article_id ORDER BY occurrences DESC;',
                        word['token'])
                    rows = cur.fetchall()

                    # calculate total count
                    total = 0
                    for row in rows:
                        total+= row[2]
                    
                    # add to list
                    for row in rows:
                        percentage = float(row[2]) / float(total)
                        if percentage >= 0.01: # TODO: threshold
                            word['disambiguations'].append({ 'percentage': percentage, 'meaning': row[1], 'id': row[0], 'articleincount': int(row[3]), 'cumulativeRelatedness': 0.0, 'overallMatch': 0.0, 'averageRelatedness': 0.0 })

                    # if no disambiguation, check if entry exists as article
                    cur.execute('SELECT id, articles.articleincount FROM articles WHERE title = %s;', word['token'])
                    row = cur.fetchone()
                    if row != None:
                        # check if already in list
                        already_found = False
                        for dis in word['disambiguations']:
                            if dis['id'] == row[0]:
                                already_found = True
                        if not already_found:
                            word['disambiguations'].append({ 'percentage': 1.0, 'meaning': word['token'], 'id': row[0], 'articleincount': int(row[1]), 'cumulativeRelatedness': 0.0, 'overallMatch': 0.0, 'averageRelatedness': 0.0 })

                    disambiguations[word['token']] = word['disambiguations']

        return disambiguations

    def __retrieve_relatedness(self, a, b):
        # retrieve ids
        cur = self._db_connection.cursor()
        #cur.execute('SELECT `id` FROM `articles` WHERE `title` = %s;', a)
        #a_id = cur.fetchone()[0]
        #cur.execute('SELECT `id` FROM `articles` WHERE `title` = %s;', b)
        #b_id = cur.fetchone()[0]

        # retrieve total counts
        #cur.execute('SELECT COUNT(*) FROM `article_links` WHERE `target_article_id` = %s;', a)
        #a_total_in = float(cur.fetchone()[0])
        #cur.execute('SELECT COUNT(*) FROM `article_links` WHERE `target_article_id` = %s;', b)
        #b_total_in = float(cur.fetchone()[0])

        a_id = a['id']
        b_id = b['id']
        a_total_in = float(a['articleincount'])
        b_total_in = float(b['articleincount'])

        if a_total_in == 0.0 or b_total_in == 0.0:
            return 0.0

        # retrieve common articles
        #cur.execute('SELECT COUNT(*) FROM (SELECT COUNT(source_article_id), source_article_id FROM (SELECT source_article_id, target_article_id FROM article_links WHERE target_article_id=%s OR target_article_id=%s) AS tmp GROUP BY source_article_id HAVING COUNT(source_article_id) > 1) AS tmp2;', 
        #    (a_id, b_id))
        cur.execute('SELECT COUNT(*) FROM (SELECT COUNT(source_article_id), source_article_id FROM links WHERE target_article_id=%s OR target_article_id=%s GROUP BY source_article_id HAVING COUNT(source_article_id) > 1) AS tmp;',
            (a_id, b_id))
        common_in = float(cur.fetchone()[0])

        # calculate relatedness
        total_articles = 4696033.0

        if common_in == 0.0:
            return 0.0

        #return common_in / (a_total_in + b_total_in) # does not work so vell in general (if stddev < 3, take other measure)

        relatedness = (math.log(max(a_total_in, b_total_in)) - math.log(common_in)) / (math.log(total_articles) - math.log(min(a_total_in, b_total_in)))
        return relatedness

    def __decide(self, words):
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
                                        relatedness = self.__retrieve_relatedness(disambiguation, disambiguation2)
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

    def run(self):
        #nouns = self.__retrieve_nouns()
        words = self.__retrieve_words()

        #disambiguations = self.__retrieve_disambiguations(nouns)
        disambiguations = self.__retrieve_disambiguations(words)

        self.__decide(words)

        outputter = HTMLOutputter()
        outputter.output(words, self._output_file)
        

        # for d in disambiguations:
        #     print d
        #     for m in disambiguations[d]:
        #         print '\t%.2f\t: %s' % (m['percentage'], m['meaning'].encode('ascii', 'ignore'))

        #print 'relatedness for (%s, %s): %.2f' % (disambiguations['orbit'][0]['meaning'].encode('ascii', 'ignore'), 
        #                                          disambiguations['Apollo'][0]['meaning'].encode('ascii', 'ignore'), 
        #                                          self.__retrieve_relatedness(disambiguations['orbit'][0]['meaning'], disambiguations['Apollo'][0]['meaning']))
        #print 'relatedness for (%s, %s): %.2f' % ('Orbit', 
        #                                          disambiguations['Apollo'][0]['meaning'].encode('ascii', 'ignore'), 
        #                                          self.__retrieve_relatedness('Orbit', disambiguations['Apollo'][0]['meaning']))



        # print 'relatedness for (%s, %s): %.2f' % (disambiguations['bar'][0]['meaning'].encode('ascii', 'ignore'), 
        #                                           disambiguations['drinks'][0]['meaning'].encode('ascii', 'ignore'), 
        #                                           self.__retrieve_relatedness(disambiguations['bar'][0]['meaning'], disambiguations['drinks'][0]['meaning']))
        # print 'relatedness for (%s, %s): %.2f' % (disambiguations['bar'][1]['meaning'].encode('ascii', 'ignore'), 
        #                                           disambiguations['drinks'][0]['meaning'].encode('ascii', 'ignore'), 
        #                                           self.__retrieve_relatedness(disambiguations['bar'][1]['meaning'], disambiguations['drinks'][0]['meaning']))
        # print 'relatedness for (%s, %s): %.2f' % (disambiguations['bar'][2]['meaning'].encode('ascii', 'ignore'), 
        #                                           disambiguations['drinks'][0]['meaning'].encode('ascii', 'ignore'), 
        #                                           self.__retrieve_relatedness(disambiguations['bar'][2]['meaning'], disambiguations['drinks'][0]['meaning']))
        # print 'relatedness for (%s, %s): %.2f' % (disambiguations['bar'][3]['meaning'].encode('ascii', 'ignore'), 
        #                                           disambiguations['drinks'][0]['meaning'].encode('ascii', 'ignore'), 
        #                                           self.__retrieve_relatedness(disambiguations['bar'][3]['meaning'], disambiguations['drinks'][0]['meaning']))
        # print 'relatedness for (%s, %s): %.2f' % (disambiguations['bar'][4]['meaning'].encode('ascii', 'ignore'), 
        #                                           disambiguations['drinks'][0]['meaning'].encode('ascii', 'ignore'), 
        #                                           self.__retrieve_relatedness(disambiguations['bar'][4]['meaning'], disambiguations['drinks'][0]['meaning']))
        # print 'relatedness for (%s, %s): %.2f' % (disambiguations['bar'][5]['meaning'].encode('ascii', 'ignore'), 
        #                                           disambiguations['drinks'][0]['meaning'].encode('ascii', 'ignore'), 
        #                                           self.__retrieve_relatedness(disambiguations['bar'][5]['meaning'], disambiguations['drinks'][0]['meaning']))

        # print 'relatedness for (%s, %s): %.2f' % (disambiguations['bar'][0]['meaning'].encode('ascii', 'ignore'), 
        #                                           disambiguations['drinks'][5]['meaning'].encode('ascii', 'ignore'), 
        #                                           self.__retrieve_relatedness(disambiguations['bar'][0]['meaning'], disambiguations['drinks'][5]['meaning']))
        # print 'relatedness for (%s, %s): %.2f' % (disambiguations['bar'][1]['meaning'].encode('ascii', 'ignore'), 
        #                                           disambiguations['drinks'][5]['meaning'].encode('ascii', 'ignore'), 
        #                                           self.__retrieve_relatedness(disambiguations['bar'][1]['meaning'], disambiguations['drinks'][5]['meaning']))
        # print 'relatedness for (%s, %s): %.2f' % (disambiguations['bar'][2]['meaning'].encode('ascii', 'ignore'), 
        #                                           disambiguations['drinks'][5]['meaning'].encode('ascii', 'ignore'), 
        #                                           self.__retrieve_relatedness(disambiguations['bar'][2]['meaning'], disambiguations['drinks'][5]['meaning']))
        # print 'relatedness for (%s, %s): %.2f' % (disambiguations['bar'][3]['meaning'].encode('ascii', 'ignore'), 
        #                                           disambiguations['drinks'][5]['meaning'].encode('ascii', 'ignore'), 
        #                                           self.__retrieve_relatedness(disambiguations['bar'][3]['meaning'], disambiguations['drinks'][5]['meaning']))
        # print 'relatedness for (%s, %s): %.2f' % (disambiguations['bar'][4]['meaning'].encode('ascii', 'ignore'), 
        #                                           disambiguations['drinks'][5]['meaning'].encode('ascii', 'ignore'), 
        #                                           self.__retrieve_relatedness(disambiguations['bar'][4]['meaning'], disambiguations['drinks'][5]['meaning']))
        # print 'relatedness for (%s, %s): %.2f' % (disambiguations['bar'][5]['meaning'].encode('ascii', 'ignore'), 
        #                                           disambiguations['drinks'][5]['meaning'].encode('ascii', 'ignore'), 
        #                                           self.__retrieve_relatedness(disambiguations['bar'][5]['meaning'], disambiguations['drinks'][5]['meaning']))


if __name__ == '__main__':
    try:
        prog = WordSenseDisambiguator(db_host='localhost')
        time.clock()
        prog.run()
        total = round(time.clock())
        minutes = total / 60
        seconds = total % 60
        print 'Finished in %d minutes and %d seconds' % (minutes, seconds)
    except mysqldb.Error, e:
        print e
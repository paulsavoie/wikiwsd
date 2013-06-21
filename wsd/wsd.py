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
        self._db_connection = mysqldb.connect(db_host, db_user, db_pass, 'wikiwsd2', charset='utf8', use_unicode=True)
        self._input_file = input_file
        self._output_file = output_file

    def __retrieve_words(self):
        # read text from input file
        f = open(self._input_file, 'r')
        text = f.read()
        f.close()

        # process text to tokenize and pos-tag it
        tokenized = nltk.word_tokenize(text)
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
                    cur.execute('SELECT target_article_id, articles.title, SUM(occurrences) AS occurrences FROM disambiguations LEFT JOIN articles ON articles.id = disambiguations.target_article_id WHERE string = %s GROUP BY target_article_id ORDER BY occurrences DESC;',
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
                            word['disambiguations'].append({ 'percentage': percentage, 'meaning': row[1], 'id': row[0] })

                    # if no disambiguation, check if entry exists as article
                    cur.execute('SELECT id FROM articles WHERE title = %s;', word['token'])
                    row = cur.fetchone()
                    if row != None:
                        word['disambiguations'].append({ 'percentage': 1.0, 'meaning': word['token'], 'id': row[0] })

                    disambiguations[word['token']] = word['disambiguations']

        return disambiguations

    def __retrieve_relatedness(self, a, b):
        # retrieve ids
        cur = self._db_connection.cursor()
        cur.execute('SELECT `id` FROM `articles` WHERE `title` = %s;', a)
        a_id = cur.fetchone()[0]
        cur.execute('SELECT `id` FROM `articles` WHERE `title` = %s;', b)
        b_id = cur.fetchone()[0]

        # retrieve total counts
        cur.execute('SELECT COUNT(*) FROM `article_links` WHERE `target_article_id` = %s;', a_id)
        a_total_in = float(cur.fetchone()[0])
        cur.execute('SELECT COUNT(*) FROM `article_links` WHERE `target_article_id` = %s;', b_id)
        b_total_in = float(cur.fetchone()[0])

        # retrieve common articles
        cur.execute('SELECT COUNT(*) FROM (SELECT COUNT(source_article_id), source_article_id FROM (SELECT source_article_id, target_article_id FROM article_links WHERE target_article_id=%s OR target_article_id=%s) AS tmp GROUP BY source_article_id HAVING COUNT(source_article_id) > 1) AS tmp2;', 
            (a_id, b_id))
        common_in = float(cur.fetchone()[0])

        # calculate relatedness
        total_articles = 4696033.0

        relatedness = (math.log(max(a_total_in, b_total_in)) - math.log(common_in)) / (math.log(total_articles) - math.log(min(a_total_in, b_total_in)))
        return relatedness


    def run(self):
        #nouns = self.__retrieve_nouns()
        words = self.__retrieve_words()

        #disambiguations = self.__retrieve_disambiguations(nouns)
        disambiguations = self.__retrieve_disambiguations(words)

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
        prog = WordSenseDisambiguator(db_host='10.11.0.101')
        time.clock()
        prog.run()
        print time.clock()
    except mysqldb.Error, e:
        print e
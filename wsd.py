"""The main program
"""

import time
import MySQLdb as mysqldb
import nltk

class WordSenseDisambiguator():
    def __init__(self, input_file='data/simpleinput.txt', output_file='data/simpleoutput.html',
            db_host='localhost', db_user='wikiwsd', db_pass='wikiwsd'):
        self._db_connection = mysqldb.connect(db_host, db_user, db_pass, 'wikiwsd', charset='utf8', use_unicode=True)
        self._input_file = input_file
        self._output_file = output_file

    def run(self):
        # read text from input file
        f = open(self._input_file, 'r')
        text = f.read()
        f.close()

        # process text to tokenize and pos-tag it
        tokenized = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokenized)

        # extract nouns
        nouns = []
        index = 0
        for token in tagged:
            word = token[0]
            tag = token[1]
            if tag[0:2] == 'NN':
                nouns.append({'token': word, 'tag': tag, 'index': index, 'length': 1})
            index+= 1

        # combine adjacent nouns
        last_index = 0
        counter = 0
        while counter < len(nouns) -1:
            noun = nouns[counter+1]
            if noun['index'] == last_index+1:
                nouns[counter]['token'] += ' ' + noun['token']
                nouns[counter]['length'] += 1
                nouns.remove(noun)
            else:
                counter = counter + 1
            last_index = noun['index']

        cur = self._db_connection.cursor()
        disambiguations = {}

        # retrieve disambiguations ordered by frequency        
        for noun in nouns:
            if disambiguations.has_key(noun['token']) == False: # only if not retrieved yet
                print 'retrieving disambiguations for %s' % (noun)
                noun_disambiguations = []

                # check if an article exists with the title of the noun and add as 100%
                
                #cur.execute('SELECT COUNT(*) FROM articles WHERE title=%s;', noun['token'])
                #result = cur.fetchone()
                #if result[0] > 0:
                #    noun_disambiguations.append({'percentage': 1.0, 'meaning': noun['token']})

                # select disambiguations
                cur.execute('SELECT COUNT(*) AS `occurrences`, `string`, `meaning` FROM `disambiguations` WHERE `string` = %s GROUP BY `string`, `meaning` ORDER BY `occurrences` DESC;', 
                    noun['token'])
                rows = cur.fetchall()

                # calculate total count
                total = 0
                for row in rows:
                    total+= row[0]
                
                
                # add to list
                for row in rows:
                    percentage = float(row[0]) / float(total)
                    if percentage >= 0.01: # TODO: threshold
                        noun_disambiguations.append({'percentage': percentage, 'meaning': row[2]})

                disambiguations[noun['token']] = noun_disambiguations

        for d in disambiguations:
            print d
            for m in disambiguations[d]:
                print '\t%.2f\t%05d: %s' % (m['percentage'], m['meaning'].encode('ascii', 'ignore'))


if __name__ == '__main__':
    try:
        prog = WordSenseDisambiguator(db_host='10.11.0.103')
        time.clock()
        prog.run()
        print time.clock()
    except mysqldb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
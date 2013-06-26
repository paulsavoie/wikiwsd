import MySQLdb as mysqldb
import logging

class MeaningFinder:
    def __init__(self, db_connection):
        self.__db_connection = db_connection

    def find_meanings(self, words):
        cur = self.__db_connection.cursor()
        disambiguations = {}

        # retrieve disambiguations ordered by frequency        
        for word in words:
            if word['isNoun']:
                if disambiguations.has_key(word['token']):
                    word['disambiguations'] = disambiguations[word['token']] 
                else: # only if not retrieved yet
                    logging.info('retrieving disambiguations for %s' % (word['token']))
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
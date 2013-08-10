# -*- coding: utf-8 -*-
'''
This file contains the code to retrieve meanings
for terms from the database

Author: Paul Laufer
Date: Jun 2013

'''

import logging

class MeaningFinder:
    '''the MeaningFinder class allows the retrieval of meanings
       for a term from the database
    '''

    '''constructor

    Arguments:
        db_connector --- a database connector (instance of wsd.DBConnector)
    '''
    def __init__(self, db_connector):
        self._db_connector = db_connector

    '''retrieves meanings and stores them in the disambiguations field as dictionary:
        - percentage --- the percentage as floating point of the commonness of this meaning
        - meaning --- the name of the meaning as string
        - id --- the id of the referenced wikipedia article of this meaning
        - articleincount --- the number of articles linking to this meaning (article)

    Arguments:
        words --- a list of dictionary entries containing the following fields:
            - token --- the token itself
            - isNoun --- boolean wheter this term can be disambiguated
            - disambiguations --- a list to which all retrieved meanings are added
    '''
    def find_meanings(self, words):
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
                    meanings = self._db_connector.retrieve_meanings(word['token'])
                    #cur.execute('SELECT target_article_id, articles.title, SUM(occurrences) as occurrences, articles.articleincount FROM disambiguations LEFT JOIN articles ON articles.id = disambiguations.target_article_id WHERE string = %s GROUP BY target_article_id ORDER BY occurrences DESC;',
                    #    word['token'])
                    #rows = cur.fetchall()

                    # calculate total count
                    total = 0
                    #for row in rows:
                    #    total+= row[2]
                    for meaning in meanings:
                        total+= meaning['occurrences']
                    
                    # add to list
                    #for row in rows:
                    for meaning in meanings:
                        if float(meaning['occurrences']) > 0 and total > 0:
                            #percentage = float(row[2]) / float(total)
                            percentage = float(meaning['occurrences'])  / float(total)
                            if percentage >= 0.02: # threshold taken from paper
                                #word['disambiguations'].append({ 'percentage': percentage, 'meaning': row[1], 'id': row[0], 'articleincount': int(row[3]), 'cumulativeRelatedness': 0.0, 'overallMatch': 0.0, 'averageRelatedness': 0.0 })
                                word['disambiguations'].append({ 'percentage': percentage, 'meaning': meaning['name'], 'id': meaning['id'], 'articleincount': meaning['articleincount'], 'cumulativeRelatedness': 0.0, 'overallMatch': 0.0, 'averageRelatedness': 0.0 })

                    # if no disambiguation, check if entry exists as article
                    #cur.execute('SELECT id, articles.articleincount FROM articles WHERE title = %s;', word['token'])
                    #row = cur.fetchone()
                    #article = self._db_connector.get_article_by_title(word['token'])
                    #if article != None:
                    #    # check if already in list
                    #    already_found = False
                    #    for dis in word['disambiguations']:
                    #        if dis['id'] == article['id']: #row[0]:
                    #            already_found = True
                    #    if not already_found:
                    #        #word['disambiguations'].append({ 'percentage': 1.0, 'meaning': word['token'], 'id': row[0], 'articleincount': int(row[1]), 'cumulativeRelatedness': 0.0, 'overallMatch': 0.0, 'averageRelatedness': 0.0 })
                    #        word['disambiguations'].append({ 'percentage': 1.0, 'meaning': word['token'], 'id': article['id'], 'articleincount': article['articleincount'], 'cumulativeRelatedness': 0.0, 'overallMatch': 0.0, 'averageRelatedness': 0.0 })

                    disambiguations[word['token']] = word['disambiguations']

        return disambiguations
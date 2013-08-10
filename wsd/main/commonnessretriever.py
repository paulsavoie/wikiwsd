# -*- coding: utf-8 -*-
'''
This file contains the code to retrieve the number of 
articles that link to both of two separate concepts

Author: Paul Laufer
Date: Jun 2013

'''

class CommonnessRetriever:
    '''class to retrieve a relatedness indicator for two meanings
    '''

    '''constructor

    Arguments:
        db_connector --- the database connector (instance of wsd.DBConnector)
    '''
    def __init__(self, db_connector):
        self._db_connector = db_connector
        self._commonness_cache = {}

    '''retrieves a commonness value between two articles

    Arguments:
        m1 --- article 1 as dictionary with field 'id'
        m2 --- article 2 as dictionary with field 'id'
    '''
    def retrieve_commonness(self, m1, m2):
        if self._commonness_cache.has_key(m1['id']) and self._commonness_cache[m1['id']].has_key(m2['id']):
            return self._commonness_cache[m1['id']][m2['id']]
        else:
            #cur = self._db_connector.cursor()
            #cur.execute('SELECT COUNT(*) FROM (SELECT COUNT(source_article_id), source_article_id FROM links WHERE target_article_id=%s OR target_article_id=%s GROUP BY source_article_id HAVING COUNT(source_article_id) > 1) AS tmp;',
            #(m1['id'], m2['id']))
            #common_in = float(cur.fetchone()[0])
            common_in = self._db_connector.retrieve_number_of_common_articles(m1['id'], m2['id'])

            if not self._commonness_cache.has_key(m1['id']):
                self._commonness_cache[m1['id']] = { }
            if not self._commonness_cache.has_key(m2['id']):
                self._commonness_cache[m2['id']] = { }
            self._commonness_cache[m1['id']][m2['id']] = common_in
            self._commonness_cache[m2['id']][m1['id']] = common_in
            return common_in

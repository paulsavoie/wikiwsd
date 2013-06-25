class CommonnessRetriever:
    def __init__(self, db_connection):
        self.__db_connection = db_connection
        self.__commonness_cache = {}

    def retrieve_commonness(self, m1, m2):
        if self.__commonness_cache.has_key(m1['id']) and self.__commonness_cache[m1['id']].has_key(m2['id']):
            return self.__commonness_cache[m1['id']][m2['id']]
        else:
            cur = self.__db_connection.cursor()
            cur.execute('SELECT COUNT(*) FROM (SELECT COUNT(source_article_id), source_article_id FROM links WHERE target_article_id=%s OR target_article_id=%s GROUP BY source_article_id HAVING COUNT(source_article_id) > 1) AS tmp;',
            (m1['id'], m2['id']))
            common_in = float(cur.fetchone()[0])

            if not self.__commonness_cache.has_key(m1['id']):
                self.__commonness_cache[m1['id']] = { }
            if not self.__commonness_cache.has_key(m2['id']):
                self.__commonness_cache[m2['id']] = { }
            self.__commonness_cache[m1['id']][m2['id']] = common_in
            self.__commonness_cache[m2['id']][m1['id']] = common_in
            return common_in

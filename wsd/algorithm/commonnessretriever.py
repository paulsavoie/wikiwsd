class CommonnessRetriever:
    '''class to retrieve a relatedness indicator for two meanings
    '''

    '''constructor

        @param work_view the work view to connect to the database
    '''
    def __init__(self, work_view):
        self._work_view = work_view
        self._commonness_cache = {}

    '''retrieves a commonness value between two articles

        @param m1 link 1 as dictionary with field 'target_article_id'
        @param m2 link 2 as dictionary with field 'target_article_id'

        @return the number of articles that link to both, article 1 and article 2
    '''
    def retrieve_commonness(self, m1, m2):
        if self._commonness_cache.has_key(m1['target_article_id']) and self._commonness_cache[m1['target_article_id']].has_key(m2['target_article_id']):
            return self._commonness_cache[m1['target_article_id']][m2['target_article_id']]
        else:

            common_in = self._work_view.retrieve_number_of_common_articles(m1['target_article_id'], m2['target_article_id'])

            if not self._commonness_cache.has_key(m1['target_article_id']):
                self._commonness_cache[m1['target_article_id']] = { }
            if not self._commonness_cache.has_key(m2['target_article_id']):
                self._commonness_cache[m2['target_article_id']] = { }
            self._commonness_cache[m1['target_article_id']][m2['target_article_id']] = common_in
            self._commonness_cache[m2['target_article_id']][m1['target_article_id']] = common_in
            
            return common_in

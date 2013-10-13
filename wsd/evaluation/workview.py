class EvaluationWorkView():
    '''The EvaluationWorkView class simulates a database work view interface
       but reduces the information taken from the database by an article under-test
       this allows cross-fold validation without rebuilding the database continously
    '''

    '''constructor

       @param work_view the original database work view to be wrapped
       @param article the article under test as dictionary with fields 'id', 'title', 'links' with subfields 'target_article_name'
                      and 'phrase'
    '''
    def __init__(self, work_view, article):
        self._work_view = work_view
        self._article = article

    def __del__(self):
        del self._work_view

    def reset_cache(self):
        self._work_view.reset_cache()

    def resolve_redirect(self, name):
        return self._work_view.resolve_redirect(name)

    def retrieve_number_of_common_articles(self, id1, id2):
        num = self._work_view.retrieve_number_of_common_articles(id1, id2)
        # if this sample article links to both, reduce the number of links accordingly
        links_to_id1 = False
        links_to_id2 = False
        for link in self._article['links']:
            if link['target_article_id'] == id1:
                links_to_id1 = True
            if link['target_article_id'] == id2:
                links_to_id2 = True
        # reduce the number of common articles by one if necessary
        if links_to_id1 and links_to_id2:
            num-= 1
        if num < 0: # should not happen, but may due to errors in db building
            num = 0
        return num

    def retrieve_meanings(self, term):
        meanings = self._work_view.retrieve_meanings(term)
        new_meanings = []
        # iterate over all meanings to check if this article influenced them
        for meaning in meanings:
            article_links_there = False
            for link in self._article['links']:
                # if this article links there, reduced the number of occurrences
                if link['target_article_id'] == meaning['id']:
                    meaning['occurrences'] -= 1
                    article_links_there = True
            # if the article links there, reduce the articleincount
            if article_links_there:
                meaning['articleincount'] -= 1
            # if no other article links to the meaning, remove it
            if meaning['articleincount'] != 0 and meaning['occurrences'] != 0:
                new_meanings.append(meaning)
        return new_meanings
        

    def resolve_title(self, title):
        # prevent the current article from being found
        result = self._work_view.resolve_title(title)
        if result == None:
            return None
        if result['id'] == self._article['id']:
            return None
        return result
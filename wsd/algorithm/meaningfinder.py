import logging

RELEVANCE_THRESHOLD = 0.02 # taken from paper

class MeaningFinder:
    '''the MeaningFinder class allows the retrieval of meanings
       for a term from the database
    '''

    '''constructor

        @param work_view a database work view to access the db
    '''
    def __init__(self, work_view):
        self._work_view = work_view

    '''retrieves meanings from the database

       @param article a dictionary containing the following fields:
           'links': a list of of dictionaries with a field 'phrase' that contains the pharse to be disambiguated
                    a further field 'meanings' will be created for each 'link' that shall hold the following subfields:
                        'target_article_id': the id of the referenced article
                        'target_article_name': the name of the referenced article
                        'relevance': a value between 0 and 1 that defines how relevant the meaning is
                        'articleincount': how many times this article is linked to
    '''
    def find_meanings(self, article):
        meanings = {}

        for link in article['links']:
            phrase = link['phrase']
            if not meanings.has_key(phrase):
                logging.info('retrieving disambiguations for %s' % (phrase))

                phrase_meanings = self._work_view.retrieve_meanings(phrase)

                # calculate total occurrences
                total = 0
                for m in phrase_meanings:
                    total += m['occurrences']

                # add to list
                result = []
                for m in phrase_meanings:
                    if total == 0: # may occur due to errors in database building
                        percentage = 1.0
                    else:
                        percentage = float(m['occurrences']) / float(total)
                    if percentage >= RELEVANCE_THRESHOLD:
                        result.append({ 
                            'target_article_id': m['id'], 
                            'target_article_name': m['name'], 
                            'relevance': percentage, 
                            'articleincount': m['articleincount']
                            })

                # cache result
                meanings[phrase] = result

            # write result
            link['meanings'] = meanings[phrase]


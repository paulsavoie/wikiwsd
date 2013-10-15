from wsd.wikipedia import NGramExtractor

AS_LINK_RATIO_THRESHOLD = 0.01

class LinkDetector:
    '''The LinkDetector class uses a database connection to retrieve possible
       links
    '''

    def __init__(self, work_view):
        '''constructor

           @param work_view the database work view to use
        '''
        self._work_view = work_view
        self._extractor = NGramExtractor()

    def detect_links(self, article):
        '''processes an article and identifies link in its text (will be marked with squared brackets)

           @param article a dictionary with a field 'text' that contains the text to be processed
        '''

        # retrieve ngrams
        ngrams = self._extractor.process(article)
        for ngram in ngrams:
            phrase = ngram[0]

            # extract occurrences for each ngram
            occurrences = self._work_view.retrieve_occurrences(phrase)

            # only if actually used as link
            if occurrences['as_link'] > 0 and occurrences['occurrences'] > 0:
                #print '%02d / %02d:\t%s' % (occurrences['occurrences'], occurrences['as_link'], phrase)

                # if it is generally more relevant as a link
                ratio = float(occurrences['as_link']) / float(occurrences['occurrences'])
                if ratio >= AS_LINK_RATIO_THRESHOLD:

                    # mark as link
                    index = 0
                    while article['text'].find(phrase, index) != -1:
                        index = article['text'].find(phrase, index)
                        # determine if inside link
                        left_start = article['text'].rfind('[[', 0, index)
                        left_end = article['text'].rfind(']]', 0, index)
                        if left_start == -1 or left_end > left_start:
                            article['text'] = article['text'][0:index] + '[[' + phrase + ']]' + article['text'][index+len(phrase):]
                        index += len(phrase)
        
        # iterate over text and extract found links in correct order
        index = 0
        while article['text'].find('[[', index) != -1:
            index = article['text'].find('[[', index)+2
            end = article['text'].find(']]', index)
            article['links'].append({ 
                'target_article_id': None, 
                'target_article_name': None, 
                'phrase': article['text'][index:end] 
                })

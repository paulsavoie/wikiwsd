import nltk
import MySQLdb as mysqldb

class TermIdentifier:
    '''class that handles the determination of tokens within a text
       which can be disambiguated (dummy version not using the database)
    '''

    '''constructor
    '''
    def __init__(self):
        self._sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

    '''identifies terms within a text for disambiguation
       
       @param text the text to be processed

       @return an article object with fields
          'id': None,
          'title': None,
          'text': The original text marked with links in double square brackets
          'links: a list of dictionaries with the following fields:
             'phrase': the text that was used as the link
             'target_article_id': None
             'target_article_name': None
    '''
    def identify_terms(self, text):
        article = {}
        sentences = self._sent_detector.tokenize(text.strip())
        links = []
        index = 0
        out_text = ''
        for sentence in sentences:
            tokenized = nltk.wordpunct_tokenize(sentence)
            tagged = nltk.pos_tag(tokenized)

            prevNoun = False
            for token in tagged:
                term = token[0]
                tag = token[1]
                if tag[0:2] == 'NN':
                    # combine adjacent nouns
                    if prevNoun:
                        out_text = out_text[:-3] + ' ' + term + ']] '
                        links[len(links)-1]['phrase']+= ' ' + term
                    else:
                        out_text += '[[%s]] ' % term
                        links.append({ 'phrase': term, 'target_article_id': None, 'target_article_name': None })
                    prevNoun = True
                else:
                    out_text += term + ' '
                    prevNoun = False

        article['type'] = 'article'
        article['id'] = None
        article['title'] = None
        article['text'] = out_text
        article['links'] = links

        return article

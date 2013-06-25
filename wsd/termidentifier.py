import nltk
import MySQLdb as mysqldb

class TermIdentifier:
    def __init__(self, db_connector):
        self.__sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self.__db_connector = db_connector

    def identify_terms(self, text):
        sentences = self.__sent_detector.tokenize(text.strip())
        terms = []
        index = 0
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
                        terms[len(terms)-1]['token'] = terms[len(terms)-1]['token'] + ' %s' % (term)
                        terms[len(terms)-1]['length'] += 1
                    else:
                        terms.append({'token': term, 'isNoun': True , 'index': index, 'length': 1, 'disambiguations': []})
                    prevNoun = True
                else:
                    terms.append({'token': term, 'isNoun': False, 'tag': tag, 'index': index, 'length': 1})
                    prevNoun = False
                index+= 1

        return terms

    # ---- SLIDING WINDOW VERSION ----

    # def __is_covered(self, terms, start, end):
    #     for term in terms:
    #         if (term['index'] >= start and term['index'] < end) or (term['index'] + term['length'] - 1 >= start and term['index'] + term['length'] - 1 < end):
    #             return True
    #     return False

    # def __is_valid_term(self, term):
    #     if len(term) < 3:
    #         return False

    #     cur = self.__db_connector.cursor()

    #     # check articles
    #     cur.execute('SELECT COUNT(*) FROM articles WHERE title=%s;', term)
    #     if cur.fetchone()[0] > 0:
    #         return True

    #     # check disambiguations
    #     cur.execute('SELECT SUM(occurrences) FROM disambiguations WHERE string=%s;', term)
    #     if cur.fetchone()[0] > 5: # need to be mentionned at least three times
    #         return True

    #     return False


    # def identify_terms(self, text):
    #     # use sliding window
    #     sentences = self.__sent_detector.tokenize(text.strip())
    #     terms = []
    #     index = 0
    #     for sentence in sentences:
    #         window_size = 6
    #         tokenized = nltk.wordpunct_tokenize(sentence)
    #         sentence_start = index
    #         while window_size > 0:
    #             start = sentence_start
    #             while (start + window_size) < len(tokenized) + sentence_start:
    #                 if not self.__is_covered(terms, start, start+window_size):
    #                     term = ' '.join(tokenized[start:start+window_size]).strip()
    #                     is_valid_term = self.__is_valid_term(term)
    #                     if is_valid_term or window_size == 1:
    #                         print '%d : %s' % (int(is_valid_term), term)
    #                         terms.append( { 'token': term, 'index': start, 'length': window_size, 'isNoun': is_valid_term, 'isValidTerm': is_valid_term, 'disambiguations': [], 'meanings': [] })
    #                 start += 1
    #             window_size -= 1
    #     return terms

if __name__ == '__main__':
    db_connection = mysqldb.connect('localhost', 'wikiwsd', 'wikiwsd', 'wikiwsd3', charset='utf8', use_unicode=True) 
    identifier = TermIdentifier(db_connection)
    identifier.identify_terms('A mouse is a small mammal belonging to the order of rodents, characteristically having a pointed snout, small rounded ears, and a long naked or almost hairless tail. The best known mouse species is the common house mouse. It is also a popular pet.')
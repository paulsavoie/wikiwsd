import logging

class EvaluationOutputter():
    def __init__(self):
        pass

    def __normalize_term(self, term):
        tokens = ['(', ')', '[', ']', "'", '"', '.', ',', '_']
        for token in tokens:
            term = term.replace(token, '')
        return term.lower()


    def output(self, tokens):
        
        total_links = 0.0
        total_correct = 0.0
        for token in tokens:
            if token.has_key('disambiguations'):
                # retrieve final disambiguation
                meanings = token['disambiguations']
                if token['finalIndex'] >= 0 and token['finalIndex'] < len(meanings):
                    final_meaning = meanings[token['finalIndex']]['meaning']
                    actual = self.__normalize_term(final_meaning)
                    expected = self.__normalize_term(token['original'])
                    if actual == expected:
                        total_correct += 1.0
                        logging.info('CORRECT got %s' % final_meaning.encode('ascii', 'ignore'))
                    else:
                        logging.info('INCORRECT: got %s, should be %s' % (final_meaning.encode('ascii', 'ignore'), token['original'].encode('ascii', 'ignore')))
                else:
                    logging.error('INCORRECT: final index %d out of range for %d meanings of word %s', token['finalIndex'], len(meanings), token['token'].encode('ascii', 'ignore'))
                total_links += 1.0       
        return {
            'total': total_links,
            'correct': total_correct,
            'ratio': total_correct / total_links
        }

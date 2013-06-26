import logging

class EvaluationOutputter():
    def __init__(self):
        pass

    def output(self, tokens):
        
        total_links = 0.0
        total_correct = 0.0
        for token in tokens:
            if token.has_key('disambiguations'):
                # retrieve final disambiguation
                meanings = token['disambiguations']
                final_meaning = meanings[token['finalIndex']]['meaning']
                logging.info('got %s, should be %s' % (final_meaning.encode('ascii', 'ignore'), token['original'].encode('ascii', 'ignore')))
                if final_meaning == token['original']:
                    total_correct += 1.0
                total_links += 1.0
        
        return {
            'total': total_links,
            'correct': total_correct,
            'ratio': total_correct / total_links
        }

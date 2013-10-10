import logging

class EvaluationOutputter():
    def __init__(self):
        pass

    def _normalize_term(self, term):
        tokens = ['(', ')', '[', ']', "'", '"', '.', ',', '_']
        for token in tokens:
            term = term.replace(token, '')
        return term.lower()


    def output(self, article):
        
        total_links = 0.0
        total_correct = 0.0
        for link in article['links']:
            if link.has_key('meanings'):
                if link['target_article_name'] == None:
                    target = '[None]'
                else:
                    target = self._normalize_term(link['target_article_name'])
                # retrieve final disambiguation
                if len(link['meanings']) > 0:
                    actual = self._normalize_term(link['meanings'][0]['target_article_name'])
                    if actual == target:
                        total_correct += 1.0
                        logging.info('CORRECT got %s' % actual)
                    else:
                        logging.info('INCORRECT: got %s, should be %s' 
                            % (actual, target))
                else:
                    logging.error('INCORRECT: no meaning found for word %s' % link['phrase'])
                total_links += 1.0
        logging.info('FINISHED: got %d of %d correct (%d%%)' % (total_correct, total_links, (100.0*total_correct/total_links)))
        return {
            'total': total_links,
            'correct': total_correct,
            'ratio': total_correct / total_links
        }

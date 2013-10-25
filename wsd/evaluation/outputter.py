import logging

class EvaluationOutputter():
    '''The EvaluationOutputter class checks for every link
       if the correct meaning was selected and logs the output accordingly
    '''

    '''constructor
    '''
    def __init__(self):
        pass

    def output_detected_links(self, article):
        '''outputs the results of an article which was evaluated
           considering the detection of links
        '''

        orig_links = article['orig_links']
        new_links = article['links']
        # apply the longest common subsequence algorithm to
        # retrieve the number of links that were correctly found

        # create "matrix"
        arr = [[0 for x in range(0, len(orig_links))] for y in range(0, len(new_links))]

        # fill matrix accordingly
        for x in range(1, len(orig_links)):
            for y in range(1, len(new_links)):
                if orig_links[x]['phrase'] == new_links[y]['phrase']:
                    arr[y][x] = arr[y-1][x-1] + 1
                else:
                    arr[y][x] = max(arr[y][x-1], arr[y-1][x])

        # backtrack the matrix to find the chosen path
        y = len(new_links) - 1
        x = len(orig_links) - 1
        while x != 0 and y != 0:
            if new_links[y]['phrase'] == orig_links[x]['phrase']:
                logging.info('CORRECT: found link %s' % new_links[y]['phrase'])
                x-= 1
                y-= 1
            else:
                if arr[y][x-1] > arr[y-1][x]:
                    logging.info('INCORRECT: did not find link %s' % orig_links[x]['phrase'])
                    x-= 1
                else:
                    logging.info('INCORRECT: found link %s, which does not exist in reference', new_links[y]['phrase'])
                    y-= 1

        correct = arr[len(new_links)-1][len(orig_links)-1]
        not_found = len(orig_links)-correct
        found_incorrect = len(new_links)-correct

        logging.info('FINISHED: got %d correct, %d found incorrectly and %d not found' % (correct, found_incorrect, not_found))

        return {
            'correct': correct,
            'total_found': len(new_links),
            'total_reference': len(orig_links)
        }

    def output_disambiguations(self, article):
        '''outputs the results of an article which was evaluated 
           considering the disambiguation of links
        '''
        
        total_links = 0.0
        total_correct = 0.0
        total_resolved = 0.0
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
                    total_resolved += 1.0
                else:
                    logging.error('INCORRECT: no meaning found for word %s' % link['phrase'])
                total_links += 1.0
        logging.info('FINISHED: got %d of %d correct (%d%%)' % (total_correct, total_links, (100.0*total_correct/total_links)))
        return {
            'total': total_links,
            'resolved': total_resolved,
            'correct': total_correct,
            'ratio': total_correct / total_links
        }

    def _normalize_term(self, term):
        tokens = ['(', ')', '[', ']', "'", '"', '.', ',', '_']
        for token in tokens:
            term = term.replace(token, '')
        return term.lower()
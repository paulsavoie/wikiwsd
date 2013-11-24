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

        orig_links = list(article['orig_links'])
        new_links = article['links']
        # apply the longest common subsequence algorithm to
        # retrieve the number of links that were correctly found

        # create "matrix"
        arr = [[0 for x in range(0, len(orig_links))] for y in range(0, len(new_links))]

        # fill matrix accordingly
        for x in range(0, len(orig_links)):
            for y in range(0, len(new_links)):
                if orig_links[x]['phrase'] == new_links[y]['phrase']:
                    prev = 0
                    if y != 0 and x != 0:
                        prev = arr[y-1][x-1]
                    arr[y][x] = prev + 1
                else:
                    prevX = 0
                    prevY = 0
                    if y != 0:
                        prevY = arr[y-1][x]
                    if x != 0:
                        prevX = arr[y][x-1]
                    arr[y][x] = max(prevX, prevY)

        # backtrack the matrix to find the chosen path
        y = len(new_links) - 1
        x = len(orig_links) - 1
        correct = 0
        while x > 0 or y > 0:
            if new_links[y]['phrase'] == orig_links[x]['phrase']:
                if len(new_links[y]['phrase']) != 0:
                    logging.info('CORRECT: found link %s' % new_links[y]['phrase'])
                    # unset new link
                    orig_links[x]['phrase'] = ''
                correct+= 1
                if x != 0:
                    x-= 1
                if y != 0:
                    y-= 1
            else:
                if y == 0:
                    logging.info('INCORRECT: did not find link %s' % orig_links[x]['phrase'])
                    x-= 1
                elif x == 0:
                    logging.info('INCORRECT: found link %s, which does not exist in reference', new_links[y]['phrase'])
                    y-= 1
                elif arr[y][x-1] > arr[y-1][x]:
                    logging.info('INCORRECT: did not find link %s' % orig_links[x]['phrase'])
                    x-= 1
                else:
                    logging.info('INCORRECT: found link %s, which does not exist in reference', new_links[y]['phrase'])
                    y-= 1

        #correct = arr[len(new_links)-1][len(orig_links)-1]
        # count original links without incorrect ones (dead end links)
        valid_orig_links_count = len(filter(lambda link: link['target_article_id'] != None, orig_links))
        not_found = valid_orig_links_count-correct
        found_incorrect = len(new_links)-correct

        logging.info('FINISHED: got %d correct, %d found incorrectly and %d not found' % (correct, found_incorrect, not_found))

        
        return {
            'correct': correct,
            'total_found': len(new_links),
            'total_reference': valid_orig_links_count
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
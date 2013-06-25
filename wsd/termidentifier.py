import nltk

class TermIdentifier:
    def __init__(self):
        pass

    def identify_terms(self, text):
        tokenized = nltk.wordpunct_tokenize(text)
        tagged = nltk.pos_tag(tokenized)

        # extract words
        words = []
        index = 0
        prevNoun = False
        for token in tagged:
            word = token[0]
            tag = token[1]
            if tag[0:2] == 'NN':
                # combine adjacent nouns
                if prevNoun:
                    words[len(words)-1]['token'] = words[len(words)-1]['token'] + ' %s' % (word)
                    words[len(words)-1]['length'] += 1
                else:
                    words.append({'token': word, 'isNoun': True, 'tag': tag, 'index': index, 'length': 1, 'disambiguations': []})
                prevNoun = True
            else:
                words.append({'token': word, 'isNoun': False, 'tag': tag, 'index': index, 'length': 1})
                prevNoun = False
            index+= 1

        return words
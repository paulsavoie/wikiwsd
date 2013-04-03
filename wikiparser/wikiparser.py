"""An tokenizer that evaluates a wikipedia article
"""

import nltk.data
from nltk.tokenize import *
import re

class WikiParser():
    def __init__(self):
        self._sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self._word_tokenizer = WordPunctTokenizer()
        self._INCORRECT_TOKENS = ('Category', 'File',
            'als', 'ast', 'zh-min-nan', 'be-x-old', 'pdc', 'hif', 'ilo', 'krc', 'lad', 'jbo', 'arz',
            'mwl', 'sah', 'sco', 'simple', 'ckb', 'fiu-vro', 'war', 'zh-yue', 'diq', 'bat-smg', 'vec',
            'vro', 'pnb', 'yue', 'bat', 'fiu' )

    def parse_article(self, article):
        links = []
        disambiguations = []
        token_index = 0

        in_link = False
        in_target = True
        current_link_token = u''
        current_link_target = u''
        end_link = False

        lines = article['text'].strip().split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 4:
                # do not consider lines only holding links # TODO: is that correct?
                if line[0] != '[' and line[-1] != ']' and line[0] != '{' and line[-1] != '}':

                    sentences = self._sent_detector.tokenize(line)
                    for sentence in sentences:
                        words = self._word_tokenizer.tokenize(sentence)

                        # search for links
                        for word in words:
                            token_index += 1
                            if len(word) >= 2 and word[0] == '[' and word[1] == '[':
                                in_link = True
                                in_target = True
                                word = word[2:]

                            # we are in a link
                            if in_link:
                                # links to files, categories or other languages are not considered
                                if word in self._INCORRECT_TOKENS or word.find(':') != -1:
                                    end_link = True
                                    word = u''
                                else:
                                    # strip word if end of link already
                                    if word.find(']]') != -1:
                                        word = word[:word.find(']]')]

                                    # if target and token are different
                                    if len(word) == 1 and word[0] == '|':
                                        in_target = False
                                        current_link_token = u''
                                    else:
                                        if in_target:
                                            current_link_target += word + u' '
                                        current_link_token += word + u' '

                            if end_link:
                                if len(current_link_target) > 0:
                                    # append link ready for entry in db
                                    links.append((article['id'], token_index, current_link_target))

                                    # if target is different from used word # TODO: maybe faster with boolean?
                                    if current_link_token != current_link_target:
                                        disambiguations.append((current_link_token, current_link_target, article['id'], token_index))

                            # clean up and prepare for next link
                            in_link = False
                            current_link_target = u''
                            current_link_token = u''
                            end_link = False

        # insert into db # TODO

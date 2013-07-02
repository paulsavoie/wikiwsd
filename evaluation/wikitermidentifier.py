import nltk.data
from nltk.tokenize import *

class WikiTermIdentifier():
    def __init__(self):
        self._sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self._word_tokenizer = WhitespaceTokenizer() #WordPunctTokenizer()
        self._INCORRECT_TOKENS = (u'Category', u'File',
            u'als', u'ast', u'zh-min-nan', u'be-x-old', u'pdc', u'hif', u'ilo',
            u'krc', u'lad', u'jbo', u'arz', u'mwl', u'sah', u'sco', u'simple', 
            u'ckb', u'fiu-vro', u'war', u'zh-yue', u'diq', u'bat-smg', u'vec', 
            u'vro', u'pnb', u'yue', u'bat', u'fiu' )

    def identify_terms(self, text):
        links = {}
        token_index = 0
        terms = []

        link_start = 0
        in_link = False
        in_target = True
        current_link_token = u''
        current_link_target = u''
        end_link = False
        invalid_link = False
        in_ref = False
        set_in_ref = False
        in_comment = False

        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()

            # remove hyphens
            line = line.replace("'''", "")
            line = line.replace("''", "")
            line = line.strip()
            if len(line) > 0 and line[0] == '*':
                line = line[1:]
                line = line.strip()

            # remove in-line-comments
            while line.find('<!--') != -1 and line.find('-->') != -1:
                line = line[:line.find('<!--')] + line[line.find('-->')+3:]

            # remove multi-line-comments
            if line.find('<!--') != -1:
                in_comment = True

            if in_comment and line.find('-->') != -1:
                line = line[line.find('-->')+3:]
                in_comment = False

            if len(line) > 4 and not in_comment and line[0] != '|' and line[0] != '{' and line[0] != ':':
                # do not consider lines only holding links

                sentences = self._sent_detector.tokenize(line)
                for sentence in sentences:
                    words = self._word_tokenizer.tokenize(sentence)

                    # search for links
                    for word in words:
                        if word.find('</ref>') != -1 or word.find('/>') != -1: # watch out - could be other tag closing 
                            in_ref = False
                            if word.find('<ref') != -1:
                                word = word[:word.find('<ref')]
                            if word.find('</ref>') != -1:
                                word = word[word.find('</ref>')+6:]
                            else:
                                if in_ref or word.find('<ref'):
                                    word = word[word.find('/>')+2:]

                        if word.find('<ref') != -1:
                            word = word[:word.find('<ref')]
                            set_in_ref = True

                        postfix = ''
                        prefix = ''
                        while len(word) > 0 and (word[-1] == '.' or word[-1] == ',' or word[-1] == '!' or word[-1] == ')' or word[-1] == '"' or word[-1] == ':'):
                            postfix = word[-1] + postfix
                            word = word[:-1]

                        while len(word) > 0 and (word[0] == '(' or word[0] == '"'):
                            prefix += word[0]
                            word = word[1:]

                        if len(word) > 0 and not in_ref and word[0] != '{' and word[-1] != '}' and word[0] != '=' and word[-1] != '=':
                            token_index += 1
                            if len(word) >= 2 and word[0] == '[' and word[1] == '[':
                                in_link = True
                                in_target = True
                                word = word[2:]
                                link_start = token_index
                            elif not in_link and not end_link:
                                # ignore links within the word
                                word = word.replace('[[', '')
                                word = word.replace(']]', '')
                                terms.append({'token': prefix + word + postfix, 'isNoun': False , 'index': token_index, 'length': 1 })


                            # we are in a link
                            if in_link:
                                # links to files, categories or other languages are not considered
                                if word.find(':') != -1 or word in self._INCORRECT_TOKENS:
                                    invalid_link = True
                                    word = u''
                                else:
                                    # strip word if end of link already
                                    if word.find(']]') != -1:
                                        postfix += word[word.find(']]')+2:]
                                        word = word[:word.find(']]')]
                                        # ignore several links in the same word
                                        word = word.replace('[[', '')
                                        word = word.replace(']]', '')
                                        end_link = True

                                    # if target and token are different
                                    separator_index = word.find('|')
                                    if separator_index != -1:
                                    #if len(word) == 1 and word[0] == '|':
                                        in_target = False
                                        current_link_target += word[:separator_index]
                                        current_link_token = word[separator_index+1:]
                                        if len(current_link_token) > 0:
                                            if not end_link:
                                                current_link_token += postfix + u' '
                                    else:
                                        if in_target and not end_link:
                                            current_link_target += word + postfix + u' '
                                        current_link_token += word + postfix + u' '
                            if end_link:
                                if len(current_link_target) > 0 and not invalid_link:
                                    
                                    current_link_token = current_link_token.strip()
                                    current_link_target = current_link_target.strip()

                                    # remove hyphens (only an anchor on page)
                                    if current_link_target.find('#') != -1:
                                        current_link_target = current_link_target[:current_link_target.find('#')]

                                    if len(current_link_target) != 0 and len(current_link_token) != 0:

                                        # append link ready for entry in db
                                        if not current_link_target in links:
                                            links[current_link_target] = 1
                                        else:
                                            links[current_link_target] += 1

                                        # if target is different from used word # TODO: maybe faster with boolean?
                                        #if current_link_token != current_link_target:
                                        # always add disambiguation
                                        #disambiguations.append((current_link_token, current_link_target))
                                        terms.append({'token': current_link_token, 'isNoun': True , 'index': link_start, 'length': (token_index - link_start), 'disambiguations': [], 'original': current_link_target })

                                # clean up and prepare for next link
                                in_link = False
                                current_link_target = u''
                                current_link_token = u''
                                end_link = False
                                invalid_link = False

                        if set_in_ref:
                            in_ref = True
                            set_in_ref = False

        return {
            "links" : links,
            "terms": terms
        }

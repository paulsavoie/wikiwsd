"""An tokenizer that evaluates a wikipedia article
"""

import nltk.data
from nltk.tokenize import *
import re
import MySQLdb as mysqldb
import logging

class WikiParser():
    def __init__(self, client, database):
        self._client = client
        self._db = client[database]
        self._sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self._word_tokenizer = WhitespaceTokenizer() #WordPunctTokenizer()
        self._INCORRECT_TOKENS = (u'Category', u'File',
            u'als', u'ast', u'zh-min-nan', u'be-x-old', u'pdc', u'hif', u'ilo',
            u'krc', u'lad', u'jbo', u'arz', u'mwl', u'sah', u'sco', u'simple', 
            u'ckb', u'fiu-vro', u'war', u'zh-yue', u'diq', u'bat-smg', u'vec', 
            u'vro', u'pnb', u'yue', u'bat', u'fiu' )

    def __resolve_article(self, title):
        article = self._db.articles.find_one( {"title": title} )
        if article == None:
            redirection_name = self._db.redirects.find_one( { "source" : title })
            if redirection_name != None:
                article = self._db.articles.find_one( { "title": redirection_name["target"] } )

        return article

    def parse_article(self, article):
        links = {}
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

            # remove hyphens
            line = line.replace("''", "")

            if len(line) > 4:
                # do not consider lines only holding links # TODO: is that correct?
                #if line[0] != '[' and line[-1] != ']' and line[0] != '{' and line[-1] != '}':

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
                            if word.find(':') != -1 or word in self._INCORRECT_TOKENS:
                                end_link = True
                                word = u''
                            else:
                                # strip word if end of link already
                                if word.find(']]') != -1:
                                    word = word[:word.find(']]')]
                                    end_link = True

                                # if target and token are different
                                separator_index = word.find('|')
                                if separator_index != -1:
                                #if len(word) == 1 and word[0] == '|':
                                    in_target = False
                                    current_link_target += word[:separator_index]
                                    current_link_token = word[separator_index+1:]
                                    if len(current_link_token) > 0:
                                        current_link_token += u' '
                                else:
                                    if in_target:
                                        current_link_target += word + u' '
                                    current_link_token += word + u' '
                        if end_link:
                            if len(current_link_target) > 0:
                                
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
                                    disambiguations.append((current_link_token, current_link_target))

                            # clean up and prepare for next link
                            in_link = False
                            current_link_target = u''
                            current_link_token = u''
                            end_link = False

        # insert into db
        # find current article
        source_article = self.__resolve_article(article['title'])

        # insert links
        for link in links:
            target_article = self.__resolve_article(link)
            if target_article == None:
                logging.error('could not find article "%s" for link update' % (link.encode('ascii', 'ignore')))
            else:
                self._db.articles.update( { "title": link }, { "$push": { "articles_link_here" : { "article": target_article['id'], "incount": links[link] } } } )

        # insert meanings
        meanings_insert = []
        for disambiguation in disambiguations:
            target_article = self.__resolve_article(disambiguation[1])
            if target_article == None:
                logging.error('could not find article "%s" for meaning update' % (disambiguation[1].encode('ascii', 'ignore')))
            else:
                self._db.meanings.update( { "string": disambiguation[0] }, { "$push": { "targets": target_article } }, upsert=True )

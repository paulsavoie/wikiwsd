# -*- coding: utf-8 -*-
'''
This file holds the code to parse read articles and 
extract the necessary information into the 
database

Author: Paul Laufer
Date: Jun 2013

'''

import nltk.data
from nltk.tokenize import *
import MySQLdb as mysqldb
import re
import logging

class NGramParser():
    """Class to parse wikipedia articles and extract useful information
    """

    """constructor

    Arguments:
        client --- the mongodb database client to use 
        db_name --- the name of the database to use
    """
    def __init__(self, db_connection):
        self._db_connection = db_connection
        self._REMOVE_PAIRS=(
            (u'{{', u'}}'),
            (u'=====', u'====='),
            (u'====', u'===='),
            (u'===', u'==='),
            (u'==', u'=='),
            (u'[http', u']'),
            (u'[File:', u']'),
            (u'[Category:', u']'),
        )
        # html tags can end with /> or </tag-name> and needs to be handled separately
        # <!-- --> comments also as they can spread multiple lines

    """parses an article

    Arguments:
        article --- a dictionary with keys 'id', 'title' and 'text'
    """
    def parse_article(self, article):
        next_line_starts_in_comment = False
        line_starts_in_comment = False

        next_line_in_tag = 0
        line_in_tag = 0
        html_tags = []

        lines = article['text'].strip().split('\n')
        new_text = ''
        for line in lines:

            # remove hyphens
            line = line.replace("'''", "")
            line = line.replace("''", "")

            line_starts_in_comment = next_line_starts_in_comment
            next_line_starts_in_comment = False

            line_in_tag = next_line_in_tag
            next_line_in_tag = 0

            # handle <!-- comments separately
            while line.find('<!--') != -1 or line_starts_in_comment:
                start = line.find('<!--')
                if line_starts_in_comment:
                    start = 0
                line_starts_in_comment = False
                pos = line.find('-->')
                if pos == -1:
                    next_line_starts_in_comment = True
                    line = line[0:start]
                else:
                    line = line[0:start] + line[pos+3:]

            # handle html tags separately
            index = 0
            outer_start_tag = line.find('<')
            if len(html_tags) != 0:
                outer_start_tag = 0
            while line.find('<', index) != -1:
                start = False
                index = line.find('<', index)+1
                end_tag = line.find('>', index)
                if line[index] == '/': # closing tag
                    if len(html_tags) != 0: # some invalid close tags appear on wikipedia - cannot do anything about that
                        html_tags.pop()
                    if len(html_tags) == 0:
                        line = line[:outer_start_tag] + line[end_tag+1:]
                        outer_start_tag = line.find('<')
                        index = 0
                else:
                    if line[end_tag-1] == '/': # simple tag
                        line = line[0:index-1] + line[end_tag+1:]
                        index-= 1
                        if index == outer_start_tag:
                            outer_start_tag = line.find('<')
                    else:
                        html_tags.append(line[index:end_tag-1])

            if len(html_tags) > 0:
                if line.find('<') != -1: # there is an opening tag somehwere
                    line = line[:line.find('<')]
                else: # everything is already within a tag
                    line = ''

            # simply ignore too short lines and those that start with incorrect token
            if len(line) > 4 and line[0:2] != ' |' and line[0] != '|' and line[0] != '!':

                # remove incorrect links
                next_link = line.find('[[')
                while next_link != -1:
                    next_colon = line.find(':', next_link)
                    next_end = line.find(']]', next_link)
                    next_start = line.find('[[', next_link+2)
                    if next_colon != -1 and (next_colon < next_end and (next_start == -1 or next_start > next_end or next_start > next_colon)): # this link is invalid
                        next_incorrect = next_link
                        count_inner = 0
                        next_end = 0
                        pos_inner = 0
                        if next_incorrect != -1:
                            # find matching end tag
                            next_end = line.find(']]', next_incorrect)
                            pos_inner = line.find('[[', next_incorrect+2)
                            last_inner = pos_inner
                            while last_inner != -1 and last_inner < next_end:
                                # find most inner link
                                while pos_inner != -1 and pos_inner < next_end:
                                    last_inner = pos_inner
                                    pos_inner = line.find('[[', pos_inner+2)
                                line = line[0:last_inner] + line[next_end+2:]
                                pos_inner = line.find('[[', next_incorrect+2)
                                last_inner = pos_inner
                                next_end = line.find(']]', next_incorrect)
                        
                            line = line[0:next_incorrect] + line[next_end+2:]
                            next_link = next_incorrect
                            # find next incorrect
                    next_link = line.find('[[', next_link+2)

                # remove pairs
                for pair in self._REMOVE_PAIRS:
                    line = self._remove_pairs(line, pair)

                # remove end of line if { in it
                if line.find('{') != -1:
                    line = line[0:line.find('{')]

                # remove empty brackets and double spaces that remained
                line = line.replace('()', '')
                line = line.replace('[]', '')
                line = line.replace('  ', ' ')
                line = line.replace('&nbsp;', ' ')

                # finally strip line
                line = line.strip(' *\r\n')

                if len(line) > 0:
                    new_text += line + '\n'

        article['text'] = new_text

    def _remove_pairs(self, line, pair):
        """removes pair recursively
        """
        length = len(pair[0])
        start = line.find(pair[0])
        end = line.find(pair[1], start+length)
        
        while start != -1 and end != -1 and start < end:
            inner = line.find(pair[0], start+length)
            if inner != -1 and inner < end: # there is an inner pair, remove first
                line = line[0:start] + self._remove_pairs(line[start+length:], pair)
            else: # remove pair itself
                line = line[0:start] + line[end+len(pair[1]):]
            start = line.find(pair[0])
            end = line.find(pair[1], start + length)
        return line

    def extract_n_grams(self, article):
        # temporarily store ngrams in structure
        ngrams = {}
        letters = 'abcdefghijklmnopqrstuvwxyz'
        for letter in letters:
            ngrams[letter] = []
        ngrams['other'] = []

        lines = article['text'].strip().split('\n')
        for line in lines:

            # remove link targets
            index = 0
            while line.find('[[', index) != -1:
                index = line.find('[[', index)+2
                end = line.find(']]', index)
                middle = line.find('|', index)
                if middle != -1 and middle < end:
                    line = line[0:index] + line[middle+1:]

            phrases = re.split(r"[!#$%&*+./:;<=>?@\^_`{}~()]", line)
            for phrase in phrases:
                phrase = phrase.strip()
                if len(phrase) > 1:
                    words = phrase.split(' ')
                    # extract n-grams
                    for size in range(1,7):
                        start = 0
                        while start < len(words) - size + 1:
                            ngram = ''
                            for i in range(0, size):
                                ngram+= words[start+i] + ' '
                            ngram = ngram.strip(' ,.:!?=_-')
                            is_link = 0
                            if len(ngram) > 4 and ngram[0:2] == '[[' and ngram[-2:] == ']]':
                                is_link = 1
                            ngram = ngram.replace('[[', '')
                            ngram = ngram.replace(']]', '')
                            start+= 1

                            if len(ngram) > 0:
                                letter = ngram[0].lower()
                                if letter in letters:
                                    ngrams[letter].append((ngram, is_link))
                                else:
                                    ngrams['other'].append((ngram, is_link))


        # iterate through ngrams and store in database
        for letter in letters:
            self._store_ngrams('ngrams_%s' % letter, ngrams[letter], article)
        self._store_ngrams('ngrams_other', ngrams['other'], article)

    def _store_ngrams(self, table, ngrams, article):
        if len(ngrams) > 0:
            retry = True
            while retry:
                retry = False
                try:
                    cursor = self._db_connection.cursor()
                    query = 'INSERT INTO %s(string, occurrences, as_link)' % (table)
                    cursor.executemany(query + ' VALUES(%s, 1, %s) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);', ngrams)
                    self._db_connection.commit()
                except mysqldb.Error, e:
                    if e.args[0] == 1213: # deadlock with other threads
                        retry = True
                    else:
                        logging.error("Error inserting ngrams of article '%s' (%d)" % (article['title'].encode('ascii', 'ignore'), article['id']))
                        logging.error("Error %d: %s" % (e.args[0],e.args[1]))

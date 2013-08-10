# -*- coding: utf-8 -*-
'''
This file offers an interface to be implemented by all
database connectors

Author: Paul Laufer
Date: Jun 2013

'''

class DBConnector():
    '''interface for database connectors
    '''

    '''constructor
    '''
    def __init__(self):
        pass

    '''retrieves a single article from the database as dictionary with fields
        id --- the id of the article
        articleincount --- the number of articles that link here
        title --- the title of the article

    Arguments:
        title --- the title of the article to be retrieved
    '''
    def get_article_by_title(self, title):
        raise NotImplementedError('Method not implemented')

    '''retrieves a single article from the database as dictionary with fields
        id --- the id of the article
        articleincount --- the number of articles that link here
        title --- the title of the article

    Arguments:
        id --- the id of the article
    '''
    def get_article_by_id(self, id):
        raise NotImplementedError('Method not implemented')

    '''checks if a redirect exists for the given link target and returns the real name
    of the target article

    Arguments:
        name --- the link target
    '''
    def resolve_redirect(self, name):
        raise NotImplementedError('Method not implemented')

    '''retrieves the number of articles that link to both target articles

        Arguments:
            id1 --- the id of target article 1
            id2 --- the id of target article 2
    '''
    def retrieve_number_of_common_articles(self, id1, id2):
        raise NotImplementedError('Method not implemented')

    '''retrieves a list of meanings for a given string as dictionary with fields
        id --- the id of the referenced article
        name --- the textual representation of the meaning
        occurrences --- the number of times this meaning occurred in the training set
        articleincount --- the number articles that link to the target concept
    '''
    def retrieve_meanings(self, name):
        raise NotImplementedError('Method not implemented')


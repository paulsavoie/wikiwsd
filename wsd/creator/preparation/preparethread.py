# -*- coding: utf-8 -*-
'''
This file holds the code to insert the article information and redirects from 
the wikipedia articles into the database

Author: Paul Laufer
Date: Jun 2013

'''

import time
import threading
import Queue
import pymongo
import logging

class PrepareThread(threading.Thread):
    """Thread which inserts the information into the mongodb database
    """

    """constructor

    Arguments:
        redirect_queue --- the queue holding the article information
        client --- a mongodb client instance used for connection
        db_name --- the database name into which the data shall be written
    """
    def __init__(self, redirect_queue, db_connection):
        threading.Thread.__init__(self)
        self._db_connection = db_connection
        self._queue = redirect_queue
        self._article_bulk = []
        self._redirect_bulk = []
        self._end = False

    def _save_bulks(self):
        try:
            if len(self._article_bulk) > 0:
                self._db.articles.insert(self._article_bulk, w=1)
            if len(self._redirect_bulk) > 0:
                self._db.redirects.insert(self._redirect_bulk, w=1)
        except pymongo.errors.DuplicateKeyError, e:
            logging.error('DuplicateKeyError: %s' % (str(e)))
        finally:
            self._redirect_bulk = []
            self._article_bulk = []

    def run(self):
        #self._client.start_request()
        while not self._end:
            try:
                cur = self._db_connection.cursor()
                vals = self._queue.get(True, 2)
                source_name = vals['source']
                target_name = vals['target']
                article_id = vals['id']

                if len(target_name) == 0: # make an insert into articles
                    cur.execute('INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(%s, NOW(), %s, %s);', 
                            (article_id, source_name.lower(), 0))
                        self._db_connection.commit()
                else:
                    cur.execute('INSERT INTO redirects(source_article_name, target_article_name) VALUES(%s, %s);', (source_name, target_name))
                    self._db_connection.commit()

                #if len(target_name) == 0:
                #    self._article_bulk.append( { "id": article_id, "title": source_name, "articles_link_here": [] } )
                #else:
                #    self._redirect_bulk.append( { "source": source_name, "target": target_name })

                #if len(self._article_bulk) >= 10 or len(self._redirect_bulk) >= 10:
                #    self._save_bulks()

                self._queue.task_done()
            except Queue.Empty:
                pass
            except mysqldb.Error, e:
                logging.error('ERROR saving redirect "%s" --> "%s"' % (source_name.encode('ascii', 'ignore'), target_name.encode('ascii', 'ignore')))
                logging.error("Error %d: %s" % (e.args[0],e.args[1]))
                self._queue.task_done()

        self._save_bulks()
        #self._client.end_request()

    def end(self):
        self._end = True

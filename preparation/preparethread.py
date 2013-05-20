"""A thread wrapper for the parser
"""

import time
import threading
import Queue
import MySQLdb as mysqldb

class PrepareThread(threading.Thread):
    def __init__(self, redirect_queue, db_connection=None):
        threading.Thread.__init__(self)
        self._db_connection = db_connection
        self._queue = redirect_queue
        self._end = False

    def run(self):
        while not self._end:
            try:
                vals = self._queue.get(True, 2)
                source_name = vals['source']
                target_name = vals['target']
                article_id = vals['id']
                cur = self._db_connection.cursor()
                if len(target_name) == 0: # make an insert into articles
                    #print 'saving new article (%s, %d)' % (source_name.encode('ascii', 'ignore'), article_id)
                    cur.execute('INSERT INTO articles(id, lastparsed, title, articleincount) VALUES(%s, NOW(), %s, %s);', 
                        (article_id, source_name, 0))
                else: # update redirects
                    #print 'saving redirect "%s" --> "%s"' % (source_name.encode('ascii', 'ignore'), target_name.encode('ascii', 'ignore'))
                    #cur.execute('INSERT INTO redirects(source_article_name, target_article_name) VALUES(%s, %s);', (source_name, target_name))
                    #self._db_connection.commit()
                self._queue.task_done()
            except Queue.Empty:
                pass
            except mysqldb.Error, e:
                print 'ERROR saving redirect "%s" --> "%s"' % (source_name.encode('ascii', 'ignore'), target_name.encode('ascii', 'ignore'))
                print "Error %d: %s" % (e.args[0],e.args[1])
                self._queue.task_done()

    def end(self):
        self._end = True

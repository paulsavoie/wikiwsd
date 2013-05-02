"""A thread wrapper for the parser
"""

import time
import threading
import Queue
import MySQLdb as mysqldb

class UpdateThread(threading.Thread):
    def __init__(self, link_queue, db_connection=None):
        threading.Thread.__init__(self)
        self._db_connection = db_connection
        self._queue = link_queue
        self._end = False

    def run(self):
        while not self._end:
            try:
                vals = self._queue.get(True, 2)
                source_id = vals[0]
                target_name = vals[1]
                #print 'updating article "%s"' % title
                cur = self._db_connection.cursor()
                #cur.execute('UPDATE articles SET linkincount = linkincount + 1 WHERE title=%s;', (title))
                cur.execute('SELECT id FROM articles WHERE title=%s;', (target_name))
                result = cur.fetchone()
                if result == None:
                    print 'ERROR: article with title "%s" not found!' % (target_name)
                else:
                    target_id = result[0]
                    cur.execute('SELECT COUNT(*) FROM article_links WHERE target_article_id=%s AND source_article_id=%s;', (target_id, source_id))
                    count = cur.fetchone()
                    if count[0] == 0:
                        cur.execute('INSERT INTO article_links (source_article_id, target_article_id, count) VALUES(%s, %s, 1);', (source_id, target_id))
                    else:
                        cur.execute('UPDATE article_links SET count = count + 1 WHERE target_article_id=%s AND source_article_id=%s;', (target_id, source_id))
                    self._db_connection.commit()
            except Queue.Empty:
                pass
            except mysqldb.Error, e:
                print "Error in article '%s'" % (title.encode('ascii', 'ignore'))
                print "Error %d: %s" % (e.args[0],e.args[1])

    def end(self):
        self._end = True

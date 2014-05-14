import MySQLdb
import logging
import time

MYSQL_DEAD_LOCK_ERROR = 1213

class MySQLBuildView:
    """The MySQLBuildView class allows database access optimized to
       build the disambiguation database
    """

    def __init__(self, db_connection):
        """constructor

           @param db_connector the database connector used to access the database
        """
        self._db_connection = db_connection
        self._cursor = db_connection.cursor()
        self.reset_cache()

    def __del__(self):
        """destructor
           closes the database connection
        """
        self._db_connection.close()

    def insert_article(self, id, title):
        """saves an article in the database

           @param id the id of the article
           @param title the title of the article 
        """
        try:
            self._cursor.execute('INSERT INTO articles(id, title) VALUES(%s, %s);', 
                (id, title))
        except MySQLdb.Error, e:
            logging.error('error saving article "%s" to database: %s (%d)' 
                % (title.encode('ascii', 'ignore'), e.args[1], e.args[0]))

    def insert_redirect(self, source_name, target_name):
        """saves a redirect in the database

        @param source_name the name of the source article
        @param target_name the name of the target article
        """
        try:
            self._cursor.execute('INSERT INTO redirects(source_article_name, target_article_name) VALUES(%s, %s);',
                (source_name, target_name))
        except MySQLdb.Error, e:
            logging.error('error saving redirect "%s" --> "%s" to database: %s (%d)' 
                % (source_name.encode('ascii', 'ignore'), target_name.encode('ascii', 'ignore'), e.args[1], e.args[0]))

    def insert_link(self, source_article_id, target_article_name):
        """saves a link to the database and updates the article record it points to

           @param source_article_id the id of the article which links to the target
           @param target_article_name the name of the target article

           @return the id of the referenced article or None if not found
        """
        target_article_id = self._resolve_title(target_article_name)
        if target_article_id == None:
            logging.error('Could not resolve target article "%s" for link from source article %d' 
                % (target_article_name.encode('ascii', 'ignore'), source_article_id))
        else:
            try:
                self._cursor.execute('INSERT INTO links(source_article_id, target_article_id) VALUES(%s, %s);',
                    (source_article_id, target_article_id))
            except MySQLdb.Error, e:
                logging.error('error saving link (%d) --> (%d) to database: %s (%d)' 
                % (source_article_id, target_article_id, e.args[1], e.args[0]))

        return target_article_id

    def insert_references(self, target_article_ids):
        """inserts references to update the linkincount field of the target article

           @param target_article_ids array of the referenced articles
        """
        retry = True
        retryCount = 0
        while retry and retryCount < 10:
            try:
                retryCount += 1
                self._cursor.executemany('UPDATE articles SET articleincount=articleincount+1 WHERE id=%s;', target_article_ids)
                retry = False
            except MySQLdb.Error, e:
                if e.args[0] == MYSQL_DEAD_LOCK_ERROR:
                    logging.warning('deadlock upading articleincount field. retrying... (%d)' % (retryCount))
                    time.sleep(0.05)
                else:
                    logging.error('error updating articleincount field for ids: ("%s"): %s (%s)'
                    % (",".join([str(id) for id in target_article_ids]),  str(e.args[1]), str(e.args[0])))

        if retry:
            logging.error('error updating articleincount field %d retries DEADLOCK when updating ids: ("%s")'
                    % (retryCount, ",".join([str(id) for id in target_article_ids])))            

    def insert_disambiguation(self, string, target_article_name):
        """saves a disambiguation to the database

           @param string the disambiguation string used for the linked entity
           @param target_article_name the name of the article the disambiguation stands for
        """
        target_article_id = self._resolve_title(target_article_name)
        if target_article_id == None:
            logging.error('Could not resolve target article "%s" for link from source article' 
                % (target_article_name.encode('ascii', 'ignore')))
        else:
            try:
                self._cursor.execute('INSERT INTO disambiguations(string, target_article_id, occurrences) VALUES(%s, %s, 1) ON DUPLICATE KEY UPDATE occurrences=occurrences+1;',
                    (string, target_article_id))
            except MySQLdb.Error, e:
                logging.error('error saving disambiguation "%s" --> %s (%d): %s (%d)'
                    % (string.encode('ascii', 'ignore'), target_article_name.encode('ascii', 'ignore'), target_article_id, e.args[1], e.args[0]))

    def insert_ngrams(self, ngrams):
        """inserts ngrams into the database

           @param ngrams a list of ngrams where each ngram is a tuple containing the string,
                         and a zero or one indicating whether it was used as a link
        """
        try:
            self._cursor.executemany('INSERT INTO ngrams(string, occurrences, as_link) VALUES(LOWER(%s), 1, %s) ON DUPLICATE KEY UPDATE occurrences=occurrences+1, as_link=as_link+VALUES(as_link);',
                    ngrams)
        except MySQLdb.Error, e:
            logging.error('error saving ngrams: %s (%d)' % (e.args[1], e.args[0]))

    def commit(self):
        '''commits the changes
        '''
        self._db_connection.commit()


    def reset_cache(self):
        """resets the internal cache and thus prevents it from growing too big
        """
        self._article_id_cache = {}

    def _resolve_title(self, title):
        """resolves an article and returns its id

           @param title the title of the article
        """
        if title in self._article_id_cache:
            return self._article_id_cache[title]

        try:
            self._cursor.execute('SELECT id FROM articles WHERE title=%s;', (title,))
            row = self._cursor.fetchone()
            if row == None:
                self._cursor.execute('SELECT id FROM articles WHERE title=(SELECT target_article_name FROM redirects WHERE source_article_name=%s);',
                        (title,))
                row = self._cursor.fetchone()

            if row == None:
                self._article_id_cache[title] = None
            else:
                self._article_id_cache[title] = row[0]
        except MySQLdb.Error, e:
            logging.error('error resolving article "%s": %s (%d)'
                % (title.encode('ascii', 'ignore'), e.args[1], e.args[0]))

        return self._article_id_cache[title]

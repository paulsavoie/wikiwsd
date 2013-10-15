import MySQLdb
import logging

class MySQLWorkView:
    """The MySQLWorkView class allows database access optimized to
       retrieve disambiguation entries from the database
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

    def reset_cache(self):
        """resets the internal cache and thus prevents it from growing too big
        """
        self._redirect_cache = {}
        self._link_cache = {}
        self._article_cache = {}
        self._occurrences_cache = {}

    def resolve_redirect(self, name):
        """resolves a redirect and returns the real article name

           @param name the name of the redirect
           
           @return the real name of the article or None if it cannot be resolved
        """
        try:
            self._cursor.execute('SELECT target_article_name FROM redirects WHERE source_article_name=%s;', name)
            row = self._cursor.fetchone()
            if row != None:
                return row[0]
        except MySQLdb.Error, e:
            logging.error('error resolving redirect for name "%s": %s (%d)' 
                % (name.encode('ascii', 'ignore'), e.args[1], e.args[0]))
        return None

    def retrieve_number_of_common_articles(self, id1, id2):
        """computes the number of articles that link to both referenced articles

            @param id1 the id of the first article to be linked to
            @param id2 the id of the second article to be linked to

            @return the number of articles that link to both referenced articles
        """
        # retrieve from database and store in cache
        try:
            if id1 not in self._link_cache:
                self._cursor.execute('SELECT source_article_id FROM links WHERE target_article_id=%s;', (id1))
                self._link_cache[id1] = self._cursor.fetchall()
            if id2 not in self._link_cache:
                self._cursor.execute('SELECT source_article_id FROM links WHERE target_article_id=%s;', (id2))
                self._link_cache[id2] = self._cursor.fetchall()
        except MySQLdb.Error, e:
            logging.error('error resolving links for source article id %d or %d: %s (%d)'
                % (id1, id2, e.args[1], e.args[0]))

        # find common articles
        counter = 0
        for source1 in self._link_cache[id1]:
            for source2 in self._link_cache[id2]:
                if source1 == source2:
                    counter += 1

        return counter

    def retrieve_meanings(self, term):
        """retrieves a set of meanings for the given term 

           @param term the term to be resolved 

           @return a list of dictionaries holding the following keys:
                'id': the id of the referenced article
                'name': the name of the referenced article
                'occurrences': the total number of times the term was used in the sense of the meaning
                'articleincount': the total number of other articles pointing to the referenced one 
        """
        meanings = []
        meanings_sorted = {}
        try:
            # TODO: change when database schema is updated
            #self._cursor.execute('SELECT target_article_id, occurrences FROM disambiguations WHERE string=%s;', term)
            self._cursor.execute('SELECT target_article_id, SUM(occurrences) AS occurrences FROM disambiguations WHERE string=%s GROUP BY target_article_id ORDER BY occurrences DESC;', term)
            result = self._cursor.fetchall()
            ids = '('
            count = 0
            for row in result:
                meanings_sorted[row[0]] = { 'id': row[0], 'occurrences': row[1] }
                ids+= '%d,' % row[0]
                count += 1
            ids = ids[:-1] + ')'
            if count == 0:
                return []
                
            # query rest of info
            self._cursor.execute('SELECT id, title, articleincount FROM articles WHERE id IN %s;' % ids)
            result = self._cursor.fetchall()
            for row in result:
                meaning = meanings_sorted[row[0]]
                meaning['title'] = row[1]
                meaning['articleincount'] = row[2]
                meanings.append(meaning)

        except MySQLdb.Error, e:
            logging.error('error retrieving meanings: %s (%d)' % (e.args[1], e.args[0]))
        return meanings

    def resolve_title(self, title):
        """resolves an article and returns it

           @param title the title of the article

           @return a dictionary with fields 'id' and 'title' or None if could not be resolved
        """
        if title in self._article_cache:
            return self._article_cache[title]

        try:
            self._cursor.execute('SELECT id, title FROM articles WHERE title=%s;', title)
            row = self._cursor.fetchone()
            if row == None:
                self._cursor.execute('SELECT id, title FROM articles WHERE title=(SELECT target_article_name FROM redirects WHERE source_article_name=%s);',
                        title)
                row = self._cursor.fetchone()

            if row == None:
                self._article_cache[title] = None
            else:
                self._article_cache[title] = { 'id': row[0], 'title': row[1] }
                if (row[1] != title):
                    self._article_cache[row[1]] = { 'id': row[0], 'title': row[1] }
        except MySQLdb.Error, e:
            logging.error('error resolving article "%s": %s (%d)'
                % (title.encode('ascii', 'ignore'), e.args[1], e.args[0]))

        return self._article_cache[title]

    def retrieve_occurrences(self, phrase):
        '''retrieves occurences of a phrase in wikipedia and how often
           they were used as a link

           @param phrase the phrase to be looked up

           @return a dictionary with two fields, 'occurrences' and 'as_link' that hold the number
                   of times the phrase was used and how often as a link
        '''

        letters = 'abcdefghijklmnopqrstuvwxyz'
        if phrase in self._occurrences_cache:
            return self._occurrences_cache[phrase]

        occurrences = { 'occurrences': 0, 'as_link': 0 }
        try:
            letter = phrase[0]
            if letter in letters:
                table = 'ngrams_%s' % letter
            else:
                table = 'ngrams_other'
            self._cursor.execute('SELECT occurrences, as_link FROM ' + table + ' WHERE string=%s;', phrase)
            
            result = self._cursor.fetchone()
            if result != None:
                occurrences['occurrences'] = result[0]
                occurrences['as_link'] = result[1]
        except MySQLdb.Error, e:
            logging.error('error retrieving occurrences for phrase "%s": %s (%d)'
                % (phrase.encode('ascii', 'ignore'), e.args[1], e.args[0]))

        self._occurrences_cache[phrase] = occurrences
        return occurrences
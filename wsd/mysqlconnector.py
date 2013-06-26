import MySQLdb as mysqldb
import threading
from dbconnector import DBConnector

class MySQLConnector(DBConnector):
    def __init__(self, host, user='wikiwsd', passwd='wikiwsd', database='wikiwsd3'):
        self.__db_connection = mysqldb.connect(host, user, passwd, database, charset='utf8', use_unicode=True)
        self.__cursor = self.__db_connection.cursor()
        self.__lock = threading.Lock()

    def get_article(self, title):
        self.__lock.acquire()
        self.__cursor.execute('SELECT id, title, articleincount FROM articles WHERE title=%s;', title)
        result = self.__cursor.fetchone()
        self.__lock.release()
        if result == None:
            return None
        return {
            'id': result[0],
            'title': result[1],
            'articleincount': int(result[2])
        }


    def resolve_redirect(self, name):
        self.__lock.acquire()
        self.__cursor.execute('SELECT target_article_name FROM redirects WHERE source_article_name=%s', name)
        result = self.__cursor.fetchone()
        self.__lock.release()
        article_name = None
        if result != None:
            article_name = result[0]
        return article_name

    def retrieve_number_of_common_articles(self, id1, id2):
        self.__lock.acquire()
        self.__cursor.execute('SELECT COUNT(*) FROM (SELECT COUNT(source_article_id), source_article_id FROM links WHERE target_article_id=%s OR target_article_id=%s GROUP BY source_article_id HAVING COUNT(source_article_id) > 1) AS tmp;', (id1, id2))
        result = self.__cursor.fetchone()
        self.__lock.release()
        num = -1.0
        if result != None:
            num = float(result[0])
        return num

    def retrieve_meanings(self, string):
        self.__lock.acquire()
        self.__cursor.execute('SELECT target_article_id, articles.title, SUM(occurrences) as occurrences, articles.articleincount FROM disambiguations LEFT JOIN articles ON articles.id = disambiguations.target_article_id WHERE string = %s GROUP BY target_article_id ORDER BY occurrences DESC;', string)
        result = self.__cursor.fetchall()
        self.__lock.release()
        if result == None:
            return result
        meanings = []
        for row in result:
            meanings.append({
                'id': row[0],
                'name': row[1],
                'occurrences': row[2],
                'articleincount': int(row[3])
            })
        return meanings
import unittest
from wsd.database import MySQLDatabase
from mysqlmocks import *

class MySQLDatabaseTest(unittest.TestCase):

    def test_build(self):
        db = MockMySQLDatabase()
        db.build()
        self.assertEqual(len(db.connection.cursor().queries), 5)
        self.assertEqual(db.connection.cursor().queries[0], 
            'CREATE TABLE `articles` ('
               '`id` BIGINT UNSIGNED NOT NULL PRIMARY KEY,'
               '`title` VARCHAR(200) NOT NULL,'
               '`articleincount` INTEGER NOT NULL DEFAULT 0,'
               'CONSTRAINT UNIQUE INDEX USING HASH(`title`)'
            ') ENGINE=InnoDB;')
        self.assertEqual(db.connection.cursor().queries[1],
            'CREATE TABLE `redirects` ('
               '`id` BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,'
               '`source_article_name` VARCHAR(200) NOT NULL,'
               '`target_article_name` VARCHAR(200) NOT NULL,'
               'CONSTRAINT UNIQUE INDEX USING HASH(`source_article_name`)'
            ') ENGINE = InnoDB;')
        self.assertEqual(db.connection.cursor().queries[2],
            'CREATE TABLE `links` ('
               '`id` BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,'
               '`source_article_id` BIGINT UNSIGNED NOT NULL,'
               '`target_article_id` BIGINT UNSIGNED NOT NULL,'
               'INDEX(`target_article_id`)'
            ') ENGINE=InnoDB;')
        self.assertEqual(db.connection.cursor().queries[3],
            'CREATE TABLE `disambiguations` ('
               '`id` BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,'
               '`string` VARCHAR(200) NOT NULL,'
               '`target_article_id` BIGINT UNSIGNED NOT NULL,'
               '`occurrences` BIGINT UNSIGNED NOT NULL DEFAULT 0,'
               'CONSTRAINT UNIQUE INDEX USING HASH(`string`, `target_article_id`)'
            ') ENGINE=InnoDB;')
        self.assertEqual(db.connection.cursor().queries[4],
            'CREATE TABLE `ngrams` ('
                '`string` VARCHAR(200) NOT NULL PRIMARY KEY,'
                '`occurrences` INT UNSIGNED NOT NULL DEFAULT 0,'
                '`as_link` INT UNSIGNED NOT NULL DEFAULT 0'
            ') ENGINE=InnoDB;')
        self.assertEqual(db.connection.closed, True)

    def test_optimize(self):
        db = MockMySQLDatabase()
        db.optimize()
        self.assertEqual(len(db.connection.cursor().queries), 5)
        self.assertEqual(db.connection.cursor().queries[0], 'OPTIMIZE TABLE articles;')
        self.assertEqual(db.connection.cursor().queries[1], 'OPTIMIZE TABLE redirects;')
        self.assertEqual(db.connection.cursor().queries[2], 'OPTIMIZE TABLE links;')
        self.assertEqual(db.connection.cursor().queries[3], 'OPTIMIZE TABLE disambiguations;')
        self.assertEqual(db.connection.cursor().queries[4], 'OPTIMIZE TABLE ngrams;')
        self.assertEqual(db.connection.closed, True)

    def test_get_build_view(self):
        db = MockMySQLDatabase()
        view = db.get_build_view()
        self.assertEqual(db.connection.closed, False)
        del view
        self.assertEqual(db.connection.closed, True)

    def test_get_work_view(self):
        db = MockMySQLDatabase()
        view = db.get_work_view()
        self.assertEqual(db.connection.closed, False)
        del view
        self.assertEqual(db.connection.closed, True)

class MockMySQLDatabase(MySQLDatabase):

    def __init__(self):
        self.connection = MockMySQLConnection()

    def _create_connection(self):
        return self.connection

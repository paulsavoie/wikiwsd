import unittest
import os
from e2e import *
from wsd.database.mysqldatabase import MySQLDatabase

'''creates an end-to-end testsuite and runs it

   @param db_host the database host 
   @param db_user the user to connect to the database
   @param db_passwd the password to connect to the database
   @param db_name the name of the database to use
'''
def e2etestsuite(db_host, db_user, db_passwd, db_name):
    # create tmp folder if not existent
    if not os.path.exists('./tmp'):
        os.mkdir('./tmp')
    failed = 0

    db = MySQLDatabase(db_host, db_user, db_passwd, db_name)

    print '### TESTING evaluation (this might take several minutes)'
    evaluationTest = EvaluationTest(db)
    if evaluationTest.test_evaluation_alkane() == False:
        failed += 1
    
    if failed == 0:
        print 'DONE - all tests passed'
    else:
        print 'FAIL - %d tests failed' % (failed)
import unittest
import os
from e2e import *

def e2etestsuite():
    # create tmp folder if not existent
    os.mkdir('./tmp')
    failed = 0

    print '### TESTING evaluation'
    evaluationTest = EvaluationTest()
    if evaluationTest.test_evaluation_alkane() == False:
        failed += 1
    
    if failed == 0:
        print 'DONE - all tests passed'
    else:
        print 'FAIL - %d tests failed' % (failed)
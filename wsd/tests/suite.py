import unittest
from . import ResolveThreadTest

def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(ResolveThreadTest, 'test'))
    #suite.addTest(ResolveThreadTest())
    return suite
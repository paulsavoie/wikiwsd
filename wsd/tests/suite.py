import unittest
from . import *

def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(ResolveThreadTest, 'test'))
    suite.addTest(unittest.makeSuite(PrepareThreadTest, 'test'))
    suite.addTest(unittest.makeSuite(ReaderTest, 'test'))
    return suite
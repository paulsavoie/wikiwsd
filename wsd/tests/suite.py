import unittest
from . import *

def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(ResolveThreadTest, 'test'))
    suite.addTest(unittest.makeSuite(PrepareThreadTest, 'test'))
    suite.addTest(unittest.makeSuite(ReaderTest, 'test'))
    suite.addTest(unittest.makeSuite(WikiParserTest, 'test'))
    return suite
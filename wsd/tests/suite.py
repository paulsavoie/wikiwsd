import unittest
from . import *

def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(ResolveThreadTest, 'test'))
    suite.addTests(unittest.makeSuite(PrepareThreadTest, 'test'))
    suite.addTests(unittest.makeSuite(ReaderTest, 'test'))
    suite.addTests(unittest.makeSuite(WikiParserTest, 'test'))
    suite.addTests(unittest.makeSuite(ReadingThreadTest, 'test'))
    suite.addTests(unittest.makeSuite(WorkingThreadTest, 'test'))
    suite.addTests(unittest.makeSuite(TermIdentifierTest, 'test'))
    suite.addTests(unittest.makeSuite(MeaningFinderTest, 'test'))
    suite.addTests(unittest.makeSuite(CommonnessRetrieverTest, 'test'))
    suite.addTests(unittest.makeSuite(RelatednessCalculatorTest, 'test'))
    suite.addTests(unittest.makeSuite(DeciderTest, 'test'))
    suite.addTests(unittest.makeSuite(HTMLOutputterTest, 'test'))
    suite.addTests(unittest.makeSuite(NGramParserTest, 'test'))
    suite.addTests(unittest.makeSuite(NGramThreadTest, 'test'))
    # evaluation
    suite.addTests(unittest.makeSuite(EvaluationConnectorTest, 'test'))
    suite.addTests(unittest.makeSuite(WikiTermIdentifierTest, 'test'))
    return suite
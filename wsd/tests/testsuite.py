import unittest
from . import *

def testsuite():
    suite = unittest.TestSuite()
    # algorithm
    suite.addTests(unittest.makeSuite(RelatednessRetrieverTest, 'test'))
    suite.addTests(unittest.makeSuite(MeaningFinderTest, 'test'))
    suite.addTests(unittest.makeSuite(RelatednessCalculatorTest, 'test'))
    
    # database
    suite.addTests(unittest.makeSuite(MySQLDatabaseTest, 'test'))
    suite.addTests(unittest.makeSuite(MySQLBuildViewTest, 'test'))
    suite.addTests(unittest.makeSuite(MySQLWorkViewTest, 'test'))
    
    suite.addTests(unittest.makeSuite(ResolveThreadTest, 'test'))
    suite.addTests(unittest.makeSuite(PrepareThreadTest, 'test'))
    suite.addTests(unittest.makeSuite(ReaderTest, 'test'))
    suite.addTests(unittest.makeSuite(WikiParserTest, 'test'))
    suite.addTests(unittest.makeSuite(ReadingThreadTest, 'test'))
    suite.addTests(unittest.makeSuite(WorkingThreadTest, 'test'))
    suite.addTests(unittest.makeSuite(TermIdentifierTest, 'test'))
    #suite.addTests(unittest.makeSuite(MeaningFinderTest, 'test'))
    #suite.addTests(unittest.makeSuite(CommonnessRetrieverTest, 'test'))
    #suite.addTests(unittest.makeSuite(RelatednessCalculatorTest, 'test'))
    suite.addTests(unittest.makeSuite(DeciderTest, 'test'))
    suite.addTests(unittest.makeSuite(HTMLOutputterTest, 'test'))
    suite.addTests(unittest.makeSuite(NGramParserTest, 'test'))
    suite.addTests(unittest.makeSuite(NGramThreadTest, 'test'))
    
    # evaluation
    suite.addTests(unittest.makeSuite(EvaluationConnectorTest, 'test'))
    suite.addTests(unittest.makeSuite(SampleReaderTest, 'test'))
    suite.addTests(unittest.makeSuite(WikiTermIdentifierTest, 'test'))
    
    # wikipedia
    suite.addTests(unittest.makeSuite(WikipediaReaderTest, 'test'))
    suite.addTests(unittest.makeSuite(WikipediaPreProcessorTest, 'test'))
    suite.addTests(unittest.makeSuite(NGramExtractorTest, 'test'))
    suite.addTests(unittest.makeSuite(LinkExtractorTest, 'test'))
    return suite
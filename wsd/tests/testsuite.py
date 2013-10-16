import unittest
from . import *

def testsuite():
    suite = unittest.TestSuite()
    # algorithm
    suite.addTests(unittest.makeSuite(RelatednessRetrieverTest, 'test'))
    suite.addTests(unittest.makeSuite(MeaningFinderTest, 'test'))
    suite.addTests(unittest.makeSuite(RelatednessCalculatorTest, 'test'))
    suite.addTests(unittest.makeSuite(DeciderTest, 'test'))
    suite.addTests(unittest.makeSuite(LinkDetectorTest, 'test'))
    
    # build
    suite.addTests(unittest.makeSuite(ArticleInserterTest, 'test'))
    suite.addTests(unittest.makeSuite(DisambiguationInserterTest, 'test'))
    suite.addTests(unittest.makeSuite(NGramInserterTest, 'test'))
    
    # database
    suite.addTests(unittest.makeSuite(MySQLDatabaseTest, 'test'))
    suite.addTests(unittest.makeSuite(MySQLBuildViewTest, 'test'))
    suite.addTests(unittest.makeSuite(MySQLWorkViewTest, 'test'))
    
    # evaluation
    suite.addTests(unittest.makeSuite(EvaluationWorkViewTest, 'test'))
    suite.addTests(unittest.makeSuite(SampleReaderTest, 'test'))
    suite.addTests(unittest.makeSuite(WikiTermIdentifierTest, 'test'))
    
    # runner
    suite.addTests(unittest.makeSuite(HTMLOutputterTest, 'test'))
    
    # wikipedia
    suite.addTests(unittest.makeSuite(WikipediaReaderTest, 'test'))
    suite.addTests(unittest.makeSuite(WikipediaPreProcessorTest, 'test'))
    suite.addTests(unittest.makeSuite(NGramExtractorTest, 'test'))
    suite.addTests(unittest.makeSuite(LinkExtractorTest, 'test'))

    return suite
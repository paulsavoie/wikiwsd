import unittest
from wsd.tests import suite

testsuite = suite()
runner = unittest.TextTestRunner()
runner.run(testsuite)
# -*- coding: utf-8 -*-
'''
This file contains the code which allows to easily test
the wsd library - by running it, all tests are executed

Author: Paul Laufer
Date: Jun 2013

'''

import unittest
import logging
from wsd.tests import testsuite

logging.disable(logging.ERROR)

suite = testsuite()
runner = unittest.TextTestRunner()
runner.run(suite)
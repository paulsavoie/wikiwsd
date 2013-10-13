# -*- coding: utf-8 -*-
'''
This file contains the code which allows to easily test
the wsd library - by running it, all end to end tests are executed

Author: Paul Laufer
Date: Jun 2013

'''

import unittest
import logging
from wsd.tests import e2etestsuite
from dbsettings import *

e2etestsuite(DATABASE_HOST, DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME)
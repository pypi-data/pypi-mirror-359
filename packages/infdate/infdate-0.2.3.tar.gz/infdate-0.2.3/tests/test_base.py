# -None*- coding: utf-8 -*-

"""
Tests for the infdate module: base functions and constants
"""

import datetime
import unittest


MAX_ORDINAL = datetime.date.max.toordinal()

# This is an error message from Python itself
NAN_INT_CONVERSION_ERROR_RE = "^cannot convert float NaN to integer$"


class VerboseTestCase(unittest.TestCase):
    """Testcase showinf maximum differences"""

    def setUp(self):
        """set maxDiff"""
        self.maxDiff = None  # pylint: disable=invalid-name ; name from unittest module

# Copyright (c) 2007-2010 testdoc authors. See LICENSE for details.

import unittest

from testdoc.finder import find_tests


class MockCollector(object):
    def __init__(self):
        self.log = []

    def got_module(self, module):
        self.log.append(('module', module))

    def got_test_class(self, klass):
        self.log.append(('class', klass))

    def got_test(self, method):
        self.log.append(('method', method))


class TestPassiveFinder(unittest.TestCase):
    """One approach to finding tests is to look inside a module for test
    classes and then look inside those test classes for test methods. The
    default finder uses this approach.
    """

    def setUp(self):
        self.collector = MockCollector()

    def test_empty(self):
        from testdoc.tests import empty
        find_tests(self.collector, empty)
        self.assertEqual(self.collector.log, [('module', empty)])

    def test_hasemptycase(self):
        from testdoc.tests import hasemptycase
        find_tests(self.collector, hasemptycase)
        self.assertEqual(
            self.collector.log, [
                ('module', hasemptycase),
                ('class', hasemptycase.SomeTest)])

    def test_hastests(self):
        from testdoc.tests import hastests
        find_tests(self.collector, hastests)
        self.assertEqual(
            self.collector.log, [
                ('module', hastests),
                ('class', hastests.SomeTest),
                ('method', hastests.SomeTest.test_foo_handles_qux),
                ('method', hastests.SomeTest.test_bar),
                ('class', hastests.AnotherTest),
                ('method', hastests.AnotherTest.test_baz)])

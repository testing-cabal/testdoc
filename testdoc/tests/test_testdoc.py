import unittest

from testdoc import find_tests


class MockFinder(object):
    def __init__(self):
        self.log = []

    def got_module(self, module):
        self.log.append(('module', module))

    def got_test_class(self, klass):
        self.log.append(('class', klass))

    def got_test(self, method):
        self.log.append(('method', method))


class TestFinder(unittest.TestCase):

    def setUp(self):
        self.finder = MockFinder()

    def test_empty(self):
        from testdoc.tests import empty
        find_tests(self.finder, empty)
        self.assertEqual(self.finder.log, [('module', empty)])

    def test_hasemptycase(self):
        from testdoc.tests import hasemptycase
        find_tests(self.finder, hasemptycase)
        self.assertEqual(
            self.finder.log, [
                ('module', hasemptycase),
                ('class', hasemptycase.SomeTest)])

    def test_hastests(self):
        from testdoc.tests import hastests
        find_tests(self.finder, hastests)
        self.assertEqual(
            self.finder.log, [
                ('module', hastests),
                ('class', hastests.SomeTest),
                ('method', hastests.SomeTest.test_foo_handles_qux),
                ('method', hastests.SomeTest.test_bar),
                ('class', hastests.AnotherTest),
                ('method', hastests.AnotherTest.test_baz)])

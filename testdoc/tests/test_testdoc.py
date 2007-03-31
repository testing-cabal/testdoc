import inspect
import unittest

from testdoc import split_name, find_tests, Documenter


class TestSplitName(unittest.TestCase):

    def test_singleWord(self):
        self.assertEqual(split_name('single'), ['single'])

    def test_underscores(self):
        self.assertEqual(split_name('split_name'), ['split', 'name'])

    def test_camelCase(self):
        self.assertEqual(split_name('splitName'), ['split', 'name'])
        self.assertEqual(
            split_name('splitLongName'), ['split', 'long', 'name'])
        self.assertEqual(split_name('splitAName'), ['split', 'a', 'name'])

    def test_camelCaseWithCaps(self):
        self.assertEqual(split_name('splitDNSName'), ['split', 'DNS', 'name'])

    def test_singleUnderscore(self):
        """Single underscores are used for reflection prefixes, so we'd like to
        ignore them.
        """
        self.assertEqual(
            split_name('test_splitName'), ['test', 'split', 'name'])

    def test_multipleUnderscores(self):
        """If there are multiple underscores, but camel case, then someone is
        probably referring to a camel-cased identifier in their name.
        """
        self.assertEqual(
            split_name('test_splitName_works'), ['test', 'splitName', 'works'])

    def test_numbers(self):
        self.assertEqual(
            split_name('test300Name'), ['test', '300', 'name'])


class MockFinder(object):
    def __init__(self):
        self.log = []

    def gotModule(self, module):
        self.log.append(('module', module))

    def gotTestClass(self, klass):
        self.log.append(('class', klass))

    def gotTest(self, method):
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


class MockFormatter(object):
    def __init__(self):
        self.log = []

    def title(self, name):
        self.log.append(('title', name))

    def section(self, name):
        self.log.append(('section', name))

    def subsection(self, name):
        self.log.append(('subsection', name))

    def paragraph(self, text):
        self.log.append(('para', text))


class TestDocumenter(unittest.TestCase):
    def setUp(self):
        self.formatter = MockFormatter()
        self.documenter = Documenter(self.formatter)

    def test_module(self):
        from testdoc.tests import empty
        self.documenter.gotModule(empty)
        self.assertEqual(
            self.formatter.log, [
                ('title', 'testdoc.tests.empty')])

    def test_emptyModuleWithDocstrings(self):
        from testdoc.tests import hastests
        self.documenter.gotModule(hastests)
        self.assertEqual(
            self.formatter.log, [
                ('title', 'testdoc.tests.hastests'),
                ('para', self.documenter.getDocs(hastests))])

    def test_emptyCase(self):
        from testdoc.tests import hastests
        self.documenter.gotTestClass(hastests.SomeTest)
        self.assertEqual(
            self.formatter.log, [
                ('section', self.documenter.titleCase(['Some'])),
                ('para', self.documenter.getDocs(hastests.SomeTest))])

    def test_method(self):
        from testdoc.tests import hastests
        self.documenter.gotTest(hastests.SomeTest.test_foo_handles_qux)
        self.assertEqual(
            self.formatter.log, [
                ('subsection',
                 self.documenter.titleCase(['Foo', 'handles', 'qux'])),
                ('para', self.documenter.getDocs(
                    hastests.SomeTest.test_foo_handles_qux))])

    def test_titleCase(self):
        self.assertEqual(
            self.documenter.titleCase(['foo', 'BAR', 'a', 'In', 'Baz', '999']),
            'Foo BAR a in Baz 999')
        self.assertEqual(
            self.documenter.titleCase(['in', 'a', 'bind']),
            'In a Bind')

    # Docstrings first, then comments, then nothing

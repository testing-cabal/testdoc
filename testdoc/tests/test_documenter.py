import unittest

from testdoc.documenter import Documenter, split_name, title_case


class TestSplitName(unittest.TestCase):

    def test_single_word(self):
        self.assertEqual(split_name('single'), ['single'])

    def test_underscores(self):
        self.assertEqual(split_name('split_name'), ['split', 'name'])

    def test_camel_case(self):
        self.assertEqual(split_name('splitName'), ['split', 'name'])
        self.assertEqual(
            split_name('splitLongName'), ['split', 'long', 'name'])
        self.assertEqual(split_name('splitAName'), ['split', 'a', 'name'])

    def test_camel_case_with_caps(self):
        self.assertEqual(split_name('splitDNSName'), ['split', 'DNS', 'name'])

    def test_single_underscore(self):
        """Single underscores are used for reflection prefixes, so we'd like to
        ignore them.
        """
        self.assertEqual(
            split_name('test_splitName'), ['test', 'split', 'name'])

    def test_multiple_underscores(self):
        """If there are multiple underscores, but camel case, then someone is
        probably referring to a camel-cased identifier in their name.
        """
        self.assertEqual(
            split_name('test_splitName_works'), ['test', 'splitName', 'works'])

    def test_numbers(self):
        self.assertEqual(
            split_name('test300Name'), ['test', '300', 'name'])


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
        self.documenter.got_module(empty)
        self.assertEqual(
            self.formatter.log,
            [('title', self.documenter.format_module('testdoc.tests.empty'))])

    def test_empty_module_with_docstrings(self):
        from testdoc.tests import hastests
        self.documenter.got_module(hastests)
        self.assertEqual(
            self.formatter.log,
            [('title',
              self.documenter.format_module('testdoc.tests.hastests')),
             ('para', self.documenter.extract_docs(hastests))])

    def test_empty_case(self):
        from testdoc.tests import hastests
        self.documenter.got_test_class(hastests.SomeTest)
        self.assertEqual(
            self.formatter.log,
            [('section', self.documenter.format_test_class('SomeTest')),
             ('para', self.documenter.extract_docs(hastests.SomeTest))])

    def test_method(self):
        from testdoc.tests import hastests
        self.documenter.got_test(hastests.SomeTest.test_foo_handles_qux)
        self.assertEqual(
            self.formatter.log,
            [('subsection',
              self.documenter.format_test('test_foo_handles_qux')),
             ('para', self.documenter.extract_docs(
            hastests.SomeTest.test_foo_handles_qux))])

    def test_title_case(self):
        self.assertEqual(
            title_case(['foo', 'BAR', 'a', 'In', 'Baz', '999', 'has']),
            'Foo BAR a in Baz 999 has')
        self.assertEqual(title_case(['in', 'a', 'bind']), 'In a Bind')

    def test_format_module(self):
        """The natural language display of a module name is just the name of
        the module.
        """
        self.assertEqual('foo.bar.baz',
                         self.documenter.format_module('foo.bar.baz'))

    def test_format_test_class(self):
        """The natural language display of a test class name is the class name
        split up into words with title-case capitalization and with all
        mentions of 'Test' stripped out.
        """
        self.assertEqual('Foo Bar',
                         self.documenter.format_test_class('TestFooBar'))
        self.assertEqual('Foo Bar',
                         self.documenter.format_test_class('FooBarTest'))


    def test_format_test(self):
        """The natural language display of a test method name is the name split
        into words with the initial word (usually 'test') dropped off. The
        phrase uses title-case capitalization.
        """
        self.assertEqual('Janey has a Gun',
                         self.documenter.format_test('test_janey_has_a_gun'))

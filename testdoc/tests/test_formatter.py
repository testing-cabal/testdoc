import StringIO
import unittest

from testdoc.formatter import WikiFormatter


class WikiFormatterTest(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO.StringIO()
        self.formatter = WikiFormatter(self.stream)

    def test_title(self):
        self.formatter.title('foo')
        self.assertEqual(self.stream.getvalue(), '= foo =\n\n')

    def test_section(self):
        self.formatter.section('foo')
        self.assertEqual(self.stream.getvalue(), '\n== foo ==\n\n')

    def test_subsection(self):
        self.formatter.subsection('foo')
        self.assertEqual(self.stream.getvalue(), '=== foo ===\n\n')

    def test_paragraph(self):
        self.formatter.paragraph('\nfoo\nbar\n')
        self.assertEqual(self.stream.getvalue(), 'foo\nbar\n\n')

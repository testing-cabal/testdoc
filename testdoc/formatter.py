"""Formatters for creating documents.

A formatter is an object which accepts an output stream (usually a file or
standard output) and then provides a structured way for writing to that stream.
All formatters should provide 'title', 'section', 'subsection' and 'paragraph'
methods which write to the stream.
"""


class WikiFormatter(object):
    """Moin formatter."""

    def __init__(self, stream):
        self.stream = stream

    def writeln(self, line):
        self.stream.write('%s\n' % (line,))

    def title(self, name):
        self.writeln('= %s =\n' % (name,))

    def section(self, name):
        self.writeln('== %s ==\n' % (name,))

    def subsection(self, name):
        self.writeln('=== %s ===\n' % (name,))

    def paragraph(self, text):
        self.writeln('%s\n' % (text.strip(),))

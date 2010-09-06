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
        self.writeln('')
        self.writeln('== %s ==\n' % (name,))

    def subsection(self, name):
        self.writeln('=== %s ===\n' % (name,))

    def paragraph(self, text):
        self.writeln('%s\n' % (text.strip(),))


class ReSTFormatter(object):
    """ReST formatter."""

    def __init__(self, stream):
        self.stream = stream

    def writeln(self, line):
        self.stream.write('%s\n' % (line,))

    def title(self, name):
        self.writeln('%s' % ('=' * len(name),))
        self.writeln('%s' % (name,))
        self.writeln('%s' % ('=' * len(name),))
        self.writeln('')
        self.writeln('.. contents::')
        self.writeln('')
        self.writeln('')

    def section(self, name):
        self.writeln('')
        self.writeln('%s' % (name,))
        self.writeln('%s' % ('=' * len(name),))
        self.writeln('')

    def subsection(self, name):
        self.writeln('%s' % (name,))
        self.writeln('%s' % ('-' * len(name),))
        self.writeln('')

    def paragraph(self, text):
        self.writeln('%s\n' % (text.strip(),))


class TrialLikeTreeFormatter(object):

    def __init__(self, stream):
        self.stream = stream
        from twisted.trial import reporter
        self._colorizer = reporter._AnsiColorizer(stream)
        self._last_indent = 0

    def write(self, line, indent, colour):
        if indent is None:
            indent = self._last_indent + 2
        else:
            self._last_indent = indent
        if colour is None:
            self.stream.write(' ' * indent + line)
        else:
            self._colorizer.write(' ' * indent + line, colour)

    def title(self, name):
        self.write(name + '\n', 0, 'green')

    def section(self, name):
        self.write(name + '\n', 2, 'yellow')

    def subsection(self, name):
        self.write(name + '\n', 4, 'white')

    def paragraph(self, text):
        for line in text.strip().splitlines(True):
            self.write(line, None, None)
        if not line.endswith('\n'):
            self.write('\n', None, None)



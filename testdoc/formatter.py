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


class ShinyFormatter(object):
    """Coloured, indented output.
    
    For use on terminals that support ANSI colour sequences.
    """

    _colours = {
        "black": "30",
        "red": "31",
        "green": "32",
        "bright green": "32;1",
        "yellow": "33",
        "bright yellow": "33;1",
        "blue": "34",
        "magenta": "35",
        "cyan": "36",
        "white": "37",
        "bright white": "37;1",
        }

    def __init__(self, stream):
        self.stream = stream
        self._last_indent = 0

    def write(self, line, indent, colour):
        if indent is None:
            indent = self._last_indent + 2
        else:
            self._last_indent = indent
        line = ' ' * indent + line
        if colour is None:
            self.stream.write(line)
        else:
            colour = self._colours[colour]
            self.stream.write('\x1b[%sm%s\x1b[0m' % (colour, line))

    def title(self, name):
        self.write(name + '\n', 0, 'bright green')

    def section(self, name):
        self.write(name + '\n', 2, 'bright yellow')

    def subsection(self, name):
        self.write(name + '\n', 4, 'bright white')

    def paragraph(self, text):
        colour = None
        if self._last_indent == 0:
            # title
            colour = 'green'
        elif self._last_indent == 2:
            # section
            colour = 'yellow'
        for line in text.strip().splitlines(True):
            self.write(line, None, colour)
        if not line.endswith('\n'):
            self.write('\n', None, colour)



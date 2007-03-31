import inspect
import re

from testdoc import reflect


def split_name(name):
    bits = name.split('_')
    if len(bits) > 2:
        return bits
    return list(gen_split_name(name))
    names = []
    for word in bits:
        names.extend(
            [bit.lower() for bit in wordRE.findall(word) if len(bit) != 0])
    return names


def gen_split_name(name,
                   wordRE=re.compile(
                       r'[0-9]+|[A-Z]?(?:(?:[A-Z](?![a-z]))+|[a-z]*)')):
    for word in name.split('_'):
        for bit in wordRE.findall(word):
            if len(bit) == 0:
                continue
            if len(bit) > 1 and bit.upper() == bit:
                yield bit
            else:
                yield bit.lower()


def get_lineno(obj):
    return inspect.getsourcelines(obj)[1]


def find_tests(finder, module):
    finder.gotModule(module)
    classes = sorted(reflect.findTestClasses(module), key=get_lineno)
    for testCaseClass in classes:
        finder.gotTestClass(testCaseClass)
        methods = [getattr(testCaseClass, 'test%s' % name)
                   for name in reflect.getTestCaseNames(testCaseClass)]
        for method in sorted(methods, key=get_lineno):
            finder.gotTest(method)


class Documenter(object):

    def __init__(self, formatter):
        self.formatter = formatter

    def titleCase(self, words):
        titled = []
        for word in words:
            if word.lower() in ['in', 'a', 'the', 'of']:
                titled.append(word.lower())
            elif word.upper() == word:
                titled.append(word)
            else:
                titled.append(word.capitalize())
        titled = ' '.join(titled)
        return titled[0].upper() + titled[1:]

    def getDocs(self, obj):
        doc = inspect.getdoc(obj)
        if doc is None:
            doc = inspect.getcomments(obj)
        return doc

    def gotModule(self, module):
        self.formatter.title(module.__name__)
        docs = self.getDocs(module)
        if docs is not None:
            self.formatter.paragraph(docs)

    def gotTestClass(self, klass):
        self.formatter.section(self.titleCase(
                [bit for bit in split_name(klass.__name__) if bit != 'test']))
        docs = self.getDocs(klass)
        if docs is not None:
            self.formatter.paragraph(docs)

    def gotTest(self, method):
        self.formatter.subsection(
            self.titleCase(split_name(method.__name__)[1:]))
        docs = self.getDocs(method)
        if docs is not None:
            self.formatter.paragraph(docs)


class WikiFormatter(object):
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


if __name__ == '__main__':
    import sys
    formatter = WikiFormatter(sys.stdout)
    documenter = Documenter(formatter)
    find_tests(documenter, reflect.namedAny(sys.argv[1]))

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


def title_case(words):
    titled = []
    for word in words:
        if word.lower() in ['in', 'a', 'the', 'of', 'has']:
            titled.append(word.lower())
        elif word.upper() == word:
            titled.append(word)
        else:
            titled.append(word.capitalize())
    titled = ' '.join(titled)
    return titled[0].upper() + titled[1:]


def get_lineno(obj):
    return inspect.getsourcelines(obj)[1]


def find_tests(finder, module):
    finder.got_module(module)
    classes = sorted(reflect.findTestClasses(module), key=get_lineno)
    for testCaseClass in classes:
        finder.got_test_class(testCaseClass)
        methods = [getattr(testCaseClass, 'test%s' % name)
                   for name in reflect.getTestCaseNames(testCaseClass)]
        for method in sorted(methods, key=get_lineno):
            finder.got_test(method)


class Documenter(object):

    def __init__(self, formatter):
        self.formatter = formatter

    def _append_docs(self, obj):
        docs = self.extract_docs(obj)
        if docs is not None:
            self.formatter.paragraph(docs)

    def extract_docs(self, obj):
        doc = inspect.getdoc(obj)
        if doc is None:
            doc = inspect.getcomments(obj)
        return doc

    def format_module(self, module_name):
        return module_name

    def format_test(self, test_name):
        return title_case(split_name(test_name)[1:])

    def format_test_class(self, class_name):
        return title_case(
            [bit for bit in split_name(class_name) if bit != 'test'])

    def got_module(self, module):
        self.formatter.title(module.__name__)
        self._append_docs(module)

    def got_test(self, method):
        self.formatter.subsection(self.format_test(method.__name__))
        self._append_docs(method)

    def got_test_class(self, klass):
        self.formatter.section(self.format_test_class(klass.__name__))
        self._append_docs(klass)

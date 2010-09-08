# Copyright (c) 2007-2010 testdoc authors. See LICENSE for details.

import re

from testdoc.reflect import extract_docs

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


class Documenter(object):

    def __init__(self, formatter):
        self.formatter = formatter

    def _append_docs(self, obj):
        docs = extract_docs(obj)
        if docs is not None:
            self.formatter.paragraph(docs)

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

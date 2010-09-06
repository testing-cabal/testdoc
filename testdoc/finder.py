import inspect

from testdoc import reflect


def get_lineno(obj):
    return inspect.getsourcelines(obj)[1]


def find_tests(finder, module):
    finder.got_module(module)
    classes = sorted(reflect.findTestClasses(module), key=get_lineno)
    for testCaseClass in classes:
        if testCaseClass.__module__ != module.__name__:
            continue
        finder.got_test_class(testCaseClass)
        methods = [getattr(testCaseClass, 'test%s' % name)
                   for name in reflect.getTestCaseNames(testCaseClass)]
        for method in sorted(methods, key=get_lineno):
            finder.got_test(method)

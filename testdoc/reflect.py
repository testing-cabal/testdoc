"""Collection of reflection tools lifted from Twisted 2.5."""

import imp
import inspect
import os
import sys
import traceback
import types


def namedAny(name):
    """Get a fully named package, module, module-global object, or attribute.
    """
    names = name.split('.')
    topLevelPackage = None
    moduleNames = names[:]
    while not topLevelPackage:
        try:
            trialname = '.'.join(moduleNames)
            topLevelPackage = __import__(trialname)
        except ImportError:
            # if the ImportError happened in the module being imported,
            # this is a failure that should be handed to our caller.
            # count stack frames to tell the difference.
            exc_info = sys.exc_info()
            if len(traceback.extract_tb(exc_info[2])) > 1:
                try:
                    # Clean up garbage left in sys.modules.
                    del sys.modules[trialname]
                except KeyError:
                    # Python 2.4 has fixed this.  Yay!
                    pass
                raise exc_info[0], exc_info[1], exc_info[2]
            moduleNames.pop()

    obj = topLevelPackage
    for n in names[1:]:
        obj = getattr(obj, n)

    return obj


def filenameToModuleName(fn):
    """
    Convert a name in the filesystem to the name of the Python module it is.

    This is agressive about getting a module name back from a file; it will
    always return a string.  Agressive means 'sometimes wrong'; it won't look
    at the Python path or try to do any error checking: don't use this method
    unless you already know that the filename you're talking about is a Python
    module.
    """
    fullName = os.path.abspath(fn)
    base = os.path.basename(fn)
    if not base:
        # this happens when fn ends with a path separator, just skit it
        base = os.path.basename(fn[:-1])
    modName = os.path.splitext(base)[0]
    while 1:
        fullName = os.path.dirname(fullName)
        if os.path.exists(os.path.join(fullName, "__init__.py")):
            modName = "%s.%s" % (os.path.basename(fullName), modName)
        else:
            break
    return modName


def samefile(filename1, filename2):
    """
    A hacky implementation of C{os.path.samefile}. Used by L{filenameToModule}
    when the platform doesn't provide C{os.path.samefile}. Do not use this.
    """
    return os.path.abspath(filename1) == os.path.abspath(filename2)


def filenameToModule(fn):
    """
    Given a filename, do whatever possible to return a module object matching
    that file.

    If the file in question is a module in Python path, properly import and
    return that module. Otherwise, load the source manually.

    @param fn: A filename.
    @return: A module object.
    @raise ValueError: If C{fn} does not exist.
    """
    if not os.path.exists(fn):
        raise ValueError("%r doesn't exist" % (fn,))
    try:
        ret = namedAny(filenameToModuleName(fn))
    except (ValueError, AttributeError):
        # Couldn't find module.  The file 'fn' is not in PYTHONPATH
        return _importFromFile(fn)
    # ensure that the loaded module matches the file
    retFile = os.path.splitext(ret.__file__)[0] + '.py'
    # not all platforms (e.g. win32) have os.path.samefile
    same = getattr(os.path, 'samefile', samefile)
    if os.path.isfile(fn) and not same(fn, retFile):
        del sys.modules[ret.__name__]
        ret = _importFromFile(fn)
    return ret


def _importFromFile(fn, moduleName=None):
    fn = _resolveDirectory(fn)
    if not moduleName:
        moduleName = os.path.splitext(os.path.split(fn)[-1])[0]
    if moduleName in sys.modules:
        return sys.modules[moduleName]
    fd = open(fn, 'r')
    try:
        module = imp.load_source(moduleName, fn, fd)
    finally:
        fd.close()
    return module


def _resolveDirectory(fn):
    if os.path.isdir(fn):
        initFile = isPackageDirectory(fn)
        if initFile:
            fn = os.path.join(fn, initFile)
        else:
            raise ValueError('%r is not a package directory' % (fn,))
    return fn


def isTestCase(obj):
    """Returns C{True} if C{obj} is a class that contains test cases, C{False}
    otherwise. Used to find all the tests in a module.
    """
    import unittest
    return (isinstance(obj, (type, types.ClassType)) and
            issubclass(obj, unittest.TestCase))


def findTestClasses(module):
    """Given a module, return all test classes"""
    for name, value in inspect.getmembers(module):
        if isTestCase(value):
            yield value


def getTestCaseNames(klass, methodPrefix='test'):
    """
    Given a class that contains C{TestCase}s, return a list of names of
    methods that probably contain tests.
    """
    return prefixedMethodNames(klass, methodPrefix)


def prefixedMethodNames(classObj, prefix):
    """A list of method names with a given prefix in a given class.
    """
    dct = {}
    addMethodNamesToDict(classObj, dct, prefix)
    return dct.keys()


def addMethodNamesToDict(classObj, dict, prefix, baseClass=None):
    """
    addMethodNamesToDict(classObj, dict, prefix, baseClass=None) -> dict
    this goes through 'classObj' (and its bases) and puts method names
    starting with 'prefix' in 'dict' with a value of 1. if baseClass isn't
    None, methods will only be added if classObj is-a baseClass

    If the class in question has the methods 'prefix_methodname' and
    'prefix_methodname2', the resulting dict should look something like:
    {"methodname": 1, "methodname2": 1}.
    """
    for base in classObj.__bases__:
        addMethodNamesToDict(base, dict, prefix, baseClass)

    if baseClass is None or baseClass in classObj.__bases__:
        for name, method in classObj.__dict__.items():
            optName = name[len(prefix):]
            if ((type(method) is types.FunctionType)
                and (name[:len(prefix)] == prefix)
                and (len(optName))):
                dict[optName] = 1


def _strip_comments(comment):
    if comment is None:
        return None
    return '\n'.join(line.strip('#').strip() for line in comment.splitlines())


def extract_docs(obj):
    doc = inspect.getdoc(obj)
    if doc is None:
        doc = _strip_comments(inspect.getcomments(obj))
    if doc is None:
        doc = _strip_comments(get_internal_comments(obj))
    return doc


def get_internal_comments(object):
    lines, lnum = inspect.findsource(object)
    if len(lines) <= lnum + 1:
        # object is probably an emply module.
        return None
    indent = inspect.indentsize(lines[lnum+1])

    comments = []
    for line in lines[lnum + 1:]:
        comment = line.strip()
        # A line is a comment if it matches the indentation the first line and
        # begins with a '#'
        if inspect.indentsize(line) == indent and comment.startswith('#'):
            comments.append(comment)
        else:
            break
    if len(comments) == 0:
        return None
    else:
        return '\n'.join(comments)

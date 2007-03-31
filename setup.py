#!/usr/bin/python

from distutils.core import setup

import testdoc

setup(
    name='testdoc',
    license='MIT',
    version=testdoc.__version__,
    description="Tool to convert Python unit tests into documentation.",
    author="Jonathan Lange",
    author_email='jml@mumak.net',
    url='https://launchpad.net/testdoc',
    packages=['testdoc'],
    scripts=['bin/testdoc'],
    long_description=("Testdoc scans unit test modules, extracting the class "
                      "and method names and converting them into natural-"
                      "language phrases, followed by whatever docstrings or "
                      "comments are in the file"))

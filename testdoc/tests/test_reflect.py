import unittest

from testdoc.reflect import extract_docs


class TestExtractDocs(unittest.TestCase):
    """Extract whatever documentation we can from Python objects.

    Python modules, classes, methods and functions can be documented in several
    ways. They can have docstrings, they can be preceded by comments, or they
    can have comments that form the first lines of their implementation.

    We want to extract whatever documentation we can from these Python blocks
    so we can include it in our documentation.
    """

    def test_no_documentation(self):
        """If the object has no documentation at all, then extract_docs should
        return None."""
        def undocumented():
            pass
        self.assertEqual(None, extract_docs(undocumented))

    def test_extracts_docstring(self):
        """If the object has a docstring, then that is the documentation we
        want to use."""

        def docstringed():
            """docstring"""
        self.assertEqual('docstring', extract_docs(docstringed))


    def test_extracts_preceding_comment(self):
        """If the object has a comment preceding it, then extract that comment.
        """

        # pre-commented
        # multi-lines
        def precommented():
            pass
        self.assertEqual('pre-commented\nmulti-lines',
                         extract_docs(precommented))

    def test_extracts_internal_comment(self):
        """If the object has a comment as part of it's internals, then extract
        that comment. The first non-comment line (even a blank one) terminates
        the comment."""

        def commented():
            # line 1
            # line 2
            #
            # line 4

            # not part of the main comment
            pass
        self.assertEqual('line 1\nline 2\n\nline 4', extract_docs(commented))

    def test_docstring_preferred(self):
        """If an object has a docstring _and_ comments, then the docstring is
        the preferred documentation.
        """

        # comment
        def docstring_and_comment():
            """docstring"""

        self.assertEqual('docstring', extract_docs(docstring_and_comment))

    def test_external_comment_preferred(self):
        """Very few people use external comments for documenting classes or
        methods. Still, if someone _is_ using external comments, they probably
        expect them to be used for documentation. Thus, the external comment is
        preferred over the internal comment.
        """

        # external
        def commented():
            # internal
            pass

        self.assertEqual('external', extract_docs(commented))

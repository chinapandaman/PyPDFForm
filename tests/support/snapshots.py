# -*- coding: utf-8 -*-

import os

from tests.support.checks import assert_same_pdf

# the user property naming an expected PDF that a test owns; reports carry it
# from pytest-xdist workers to the controller, which sees every owner
OWNED = "expected_pdf"


class ExpectPdf:
    # compares a test's output with an expected PDF, and records the output to
    # write when expected PDFs are regenerated

    def __init__(self, node, root, standard_zlib):
        self.node = node
        self.root = root
        self.standard_zlib = standard_zlib
        # the outputs to regenerate, by the path of their expected PDF
        self.outputs = {}

    def __call__(
        self, stream, path=None, *, same_as=None, timestamped=False, length_only=False
    ):
        # path is the expected PDF this test owns and regenerates; same_as is
        # only compared, for example one that another test owns
        if (path is None) == (same_as is None):
            msg = "expect_pdf takes either path or same_as"
            raise TypeError(msg)
        if length_only and same_as is None:
            msg = "length_only only applies to same_as"
            raise TypeError(msg)

        if path is not None:
            path = os.path.abspath(path)
            owned = os.path.relpath(path, self.root).replace(os.sep, "/")
            self.node.user_properties.append((OWNED, owned))
            # recorded before comparing, so that a failing test is regenerated
            self.outputs[path] = stream

        with open(path or same_as, "rb") as f:
            expected = f.read()

        if length_only:
            # the objects differ, for example because they are numbered differently
            if self.standard_zlib:
                assert len(stream) == len(expected)
            return

        assert_same_pdf(stream, expected, self.standard_zlib, timestamped)
        if timestamped and path is not None:
            # a timestamped PDF is regenerated only when it changed
            del self.outputs[path]

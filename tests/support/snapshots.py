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
        super().__init__()
        self.node = node
        self.root = root
        self.standard_zlib = standard_zlib
        # the outputs to regenerate, by the path of their expected PDF
        self.outputs = {}
        # the outputs that differ from an expected PDF compared with same_as,
        # which a comparison run shows without regenerating that PDF
        self.mismatches = {}

    def __call__(
        self, stream, path=None, *, same_as=None, timestamped=False, length_only=False
    ):
        # path is the expected PDF this test owns and regenerates; same_as is
        # only compared, for example one that another test owns
        if length_only and same_as is None:
            msg = "length_only only applies to same_as"
            raise TypeError(msg)
        if path is not None and same_as is None:
            expected_path = os.path.abspath(path)
            owned = os.path.relpath(expected_path, self.root).replace(os.sep, "/")
            self.node.user_properties.append((OWNED, owned))
            # recorded before comparing, so that a failing test is regenerated
            self.outputs[expected_path] = stream
        elif path is None and same_as is not None:
            expected_path = os.path.abspath(same_as)
        else:
            msg = "expect_pdf takes either path or same_as"
            raise TypeError(msg)

        with open(expected_path, "rb") as f:
            expected = f.read()

        try:
            if length_only:
                # the objects differ, for example because they are numbered
                # differently
                if self.standard_zlib:
                    assert len(stream) == len(expected)
            else:
                assert_same_pdf(stream, expected, self.standard_zlib, timestamped)
        except Exception:
            if path is None:
                self.mismatches[expected_path] = stream
            raise

        if timestamped and path is not None:
            # a timestamped PDF is regenerated only when it changed
            del self.outputs[expected_path]

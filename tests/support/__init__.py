# -*- coding: utf-8 -*-

import pytest

# the support modules assert, so pytest rewrites them to report the values
# involved; they must be registered before they are imported
pytest.register_assert_rewrite("tests.support.checks", "tests.support.snapshots")

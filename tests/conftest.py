# -*- coding: utf-8 -*-

import os
import sys

import pytest


@pytest.fixture(scope="session", autouse=True)
def add_root_to_path():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",))

# -*- coding: utf-8 -*-

import pytest
import pdfrw
from copy import deepcopy

from PyPDFForm.core.utils import Utils


@pytest.fixture
def data_dict():
    return {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    }


def test_bool_to_checkboxes(data_dict):
    result = deepcopy(data_dict)

    for k, v in Utils().bool_to_checkboxes(result).items():
        if isinstance(data_dict[k], bool):
            assert v == (pdfrw.PdfName.Yes if data_dict[k] else pdfrw.PdfName.Off)

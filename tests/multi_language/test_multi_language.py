# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_zh_cn(zh_cn, expect_pdf):
    expected_path = os.path.join(zh_cn, "test_zh_cn.pdf")
    obj = PdfWrapper(os.path.join(zh_cn, "zh_cn.pdf")).fill(
        {
            "投资者名称": "张三",
            "基金账户": "央行",
        },
    )

    expect_pdf(obj.read(), expected_path)


def test_ko(ko, expect_pdf):
    expected_path = os.path.join(ko, "test_ko.pdf")
    obj = PdfWrapper(os.path.join(ko, "ko.pdf")).fill(
        {
            "상호": "한국",
            "성명": "홍길동",
        },
    )

    expect_pdf(obj.read(), expected_path)

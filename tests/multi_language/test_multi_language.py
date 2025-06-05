# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_zh_cn(zh_cn, request):
    expected_path = os.path.join(
        zh_cn, "test_zh_cn.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(os.path.join(zh_cn, "zh_cn.pdf")).fill(
            {
                "投资者名称": "张三",
                "基金账户": "央行",
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected

def test_korean_simplified(multi_language_pdf_samples, request):
    expected_path = os.path.join(
        multi_language_pdf_samples, "test_korean_simplified.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(os.path.join(multi_language_pdf_samples, "ko_kr.pdf")).fill(
            {
                "상호": "한국",
                "성명": "홍길동",
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected

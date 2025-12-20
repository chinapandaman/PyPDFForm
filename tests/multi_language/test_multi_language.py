# -*- coding: utf-8 -*-

import os

from PyPDFForm import Fields, PdfWrapper


def test_zh_cn(zh_cn, request):
    expected_path = os.path.join(zh_cn, "test_zh_cn.pdf")
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


def test_ko(ko, request):
    expected_path = os.path.join(ko, "test_ko.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(os.path.join(ko, "ko.pdf")).fill(
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


def test_ja(ja, pdf_samples, request):
    expected_path = os.path.join(ja, "test_ja.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("こんにちは", 1, 100, 100))
            .fill({"こんにちは": "さよなら"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_ru(ru, pdf_samples, request):
    expected_path = os.path.join(ru, "test_ru.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("привет", 1, 100, 100))
            .fill({"привет": "пока"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_vi(vi, pdf_samples, request):
    expected_path = os.path.join(vi, "test_vi.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("Xin chào", 1, 100, 100))
            .fill({"Xin chào": "Tạm biệt"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_es(es, pdf_samples, request):
    expected_path = os.path.join(es, "test_es.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("Hola", 1, 100, 100))
            .fill({"Hola": "Adiós"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_it(it, pdf_samples, request):
    expected_path = os.path.join(it, "test_it.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("Ciao", 1, 100, 100))
            .fill({"Ciao": "Arrivederci"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected

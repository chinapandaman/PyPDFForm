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


def test_hi(hi, pdf_samples, request):
    expected_path = os.path.join(hi, "test_hi.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("नमस्ते", 1, 100, 100))
            .fill({"नमस्ते": "अलविदा"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_tr(tr, pdf_samples, request):
    expected_path = os.path.join(tr, "test_tr.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("Merhaba", 1, 100, 100))
            .fill({"Merhaba": "Güle güle"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_ar(ar, pdf_samples, request):
    expected_path = os.path.join(ar, "test_ar.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("مرحباً", 1, 100, 100))
            .fill({"مرحباً": "مع السلامة"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_de(de, pdf_samples, request):
    expected_path = os.path.join(de, "test_de.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("Hallo", 1, 100, 100))
            .fill({"Hallo": "Auf Wiedersehen"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fr(fr, pdf_samples, request):
    expected_path = os.path.join(fr, "test_fr.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("Bonjour", 1, 100, 100))
            .fill({"Bonjour": "Au revoir"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_jv(jv, pdf_samples, request):
    expected_path = os.path.join(jv, "test_jv.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("Sugeng enjing", 1, 100, 100))
            .fill({"Sugeng enjing": "Sugeng dalu"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_th(th, pdf_samples, request):
    expected_path = os.path.join(th, "test_th.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("สวัสดี", 1, 100, 100))
            .fill({"สวัสดี": "ลาก่อน"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_he(he, pdf_samples, request):
    expected_path = os.path.join(he, "test_he.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("שלום", 1, 100, 100))
            .fill({"שלום": "להתראות"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fa(fa, pdf_samples, request):
    expected_path = os.path.join(fa, "test_fa.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("سلام", 1, 100, 100))
            .fill({"سلام": "خداحافظ"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_pl(pl, pdf_samples, request):
    expected_path = os.path.join(pl, "test_pl.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("Cześć", 1, 100, 100))
            .fill({"Cześć": "Do widzenia"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_sr(sr, pdf_samples, request):
    expected_path = os.path.join(sr, "test_sr.pdf")
    with open(expected_path, "rb+") as f:
        obj = (
            PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
            .create_field(Fields.TextField("Здраво", 1, 100, 100))
            .fill({"Здраво": "Довиђења"})
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected

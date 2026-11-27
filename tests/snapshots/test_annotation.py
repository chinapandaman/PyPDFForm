# -*- coding: utf-8 -*-

import os

from PyPDFForm import Annotations, PdfWrapper


def test_annotate(template_stream, expect_pdf):
    obj = PdfWrapper(template_stream).annotate(
        [
            Annotations.TextAnnotation(1, 100, 100, contents="this is an annotation"),
            Annotations.TextAnnotation(
                1,
                200,
                100,
                contents="this is a second annotation",
                title="Annotation 2",
                icon=Annotations.TextAnnotation.comment_icon,
            ),
            Annotations.TextAnnotation(
                1,
                100,
                200,
                contents="this is a third annotation",
                icon=Annotations.TextAnnotation.help_icon,
            ),
            Annotations.TextAnnotation(
                1,
                200,
                200,
                contents="this is a forth annotation",
                icon=Annotations.TextAnnotation.key_icon,
            ),
            Annotations.TextAnnotation(
                2,
                100,
                300,
                contents="this is a fifth annotation",
                icon=Annotations.TextAnnotation.insert_icon,
            ),
        ]
    )

    expect_pdf(obj.read())


def test_annotate_no_annotations(pdf_samples, expect_pdf):
    obj = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf")).annotate(
        [
            Annotations.TextAnnotation(1, 100, 100, contents="this is an annotation"),
            Annotations.TextAnnotation(
                1,
                200,
                100,
                contents="this is a second annotation",
                title="Annotation 2",
                icon=Annotations.TextAnnotation.comment_icon,
            ),
            Annotations.TextAnnotation(
                1,
                100,
                200,
                contents="this is a third annotation",
                icon=Annotations.TextAnnotation.help_icon,
            ),
            Annotations.TextAnnotation(
                1,
                200,
                200,
                contents="this is a forth annotation",
                icon=Annotations.TextAnnotation.key_icon,
            ),
            Annotations.TextAnnotation(
                1,
                100,
                300,
                contents="this is a fifth annotation",
                icon=Annotations.TextAnnotation.insert_icon,
            ),
        ]
    )

    expect_pdf(obj.read())


def test_rubber_stamp_annotation(template_stream, expect_pdf):
    obj = PdfWrapper(template_stream).annotate(
        [
            Annotations.RubberStampAnnotation(
                1,
                0,
                400,
                width=50,
                height=50,
                name=Annotations.RubberStampAnnotation.approved,
            ),
            Annotations.RubberStampAnnotation(
                1,
                100,
                400,
                width=50,
                height=50,
                name=Annotations.RubberStampAnnotation.experimental,
            ),
            Annotations.RubberStampAnnotation(
                1,
                200,
                400,
                width=50,
                height=50,
                name=Annotations.RubberStampAnnotation.not_approved,
            ),
            Annotations.RubberStampAnnotation(
                1,
                300,
                400,
                width=50,
                height=50,
                name=Annotations.RubberStampAnnotation.as_is,
            ),
            Annotations.RubberStampAnnotation(
                1,
                400,
                400,
                width=50,
                height=50,
                name=Annotations.RubberStampAnnotation.expired,
            ),
            Annotations.RubberStampAnnotation(
                1,
                0,
                500,
                width=50,
                height=50,
                name=Annotations.RubberStampAnnotation.not_for_public_release,
            ),
            Annotations.RubberStampAnnotation(
                1,
                100,
                500,
                width=50,
                height=50,
                name=Annotations.RubberStampAnnotation.confidential,
            ),
            Annotations.RubberStampAnnotation(
                1,
                200,
                500,
                width=50,
                height=50,
                name=Annotations.RubberStampAnnotation.final,
            ),
            Annotations.RubberStampAnnotation(
                1,
                300,
                500,
                width=50,
                height=50,
                name=Annotations.RubberStampAnnotation.sold,
            ),
            Annotations.RubberStampAnnotation(
                1,
                400,
                500,
                width=50,
                height=50,
                name=Annotations.RubberStampAnnotation.departmental,
            ),
            Annotations.RubberStampAnnotation(
                1,
                0,
                600,
                width=50,
                height=50,
                name=Annotations.RubberStampAnnotation.for_comment,
            ),
            Annotations.RubberStampAnnotation(
                1,
                100,
                600,
                width=50,
                height=50,
                name=Annotations.RubberStampAnnotation.top_secret,
            ),
            Annotations.RubberStampAnnotation(
                1,
                200,
                600,
                width=50,
                height=50,
                name=Annotations.RubberStampAnnotation.draft,
            ),
            Annotations.RubberStampAnnotation(
                1,
                300,
                600,
                width=50,
                height=50,
                name=Annotations.RubberStampAnnotation.for_public_release,
            ),
        ]
    )

    expect_pdf(obj.read())

"""Deprecated PyPDFForm class."""

from .middleware.constants import DEPRECATION_NOTICE

raise DeprecationWarning(
    DEPRECATION_NOTICE.format("PyPDFForm.PyPDFForm", "1.4.0", "PyPDFForm.PdfWrapper")
)

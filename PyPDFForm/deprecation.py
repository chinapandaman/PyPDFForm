# -*- coding: utf-8 -*-

from warnings import warn

from .constants import DEPRECATION_NOTICE


def deprecation_notice(to_deprecate: str, to_replace: str) -> None:
    warn(
        DEPRECATION_NOTICE.format(
            to_deprecate,
            to_replace,
        ),
        DeprecationWarning,  # noqa: PT030
        stacklevel=2,
    )

# -*- coding: utf-8 -*-
"""
Reports whether the active Python zlib module uses zlib or zlib-ng.
"""

import sys
import zlib

ZLIB_NG = "zlib-ng"


def zlib_backend():
    versions = [zlib.ZLIB_VERSION, getattr(zlib, "ZLIB_RUNTIME_VERSION", "")]
    if any(ZLIB_NG in version.lower() for version in versions):
        return ZLIB_NG

    return "zlib"


if __name__ == "__main__":
    print(f"Python executable: {sys.executable}")
    print(f"zlib compile-time version: {zlib.ZLIB_VERSION}")
    print(f"zlib runtime version: {getattr(zlib, 'ZLIB_RUNTIME_VERSION', 'unknown')}")
    print(f"zlib backend: {zlib_backend()}")

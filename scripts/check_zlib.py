# -*- coding: utf-8 -*-
"""
Reports structured information about the active Python zlib module.
"""

import json
import sys
import zlib

ZLIB_NG = "zlib-ng"


def zlib_backend():
    versions = [zlib.ZLIB_VERSION, getattr(zlib, "ZLIB_RUNTIME_VERSION", "")]
    if any(ZLIB_NG in version.lower() for version in versions):
        return ZLIB_NG

    return "zlib"


def zlib_info():
    return {
        "python_executable": sys.executable,
        "zlib_backend": zlib_backend(),
        "zlib_compile_time_version": zlib.ZLIB_VERSION,
        "zlib_runtime_version": getattr(zlib, "ZLIB_RUNTIME_VERSION", "unknown"),
    }


def main():
    print(json.dumps(zlib_info(), sort_keys=True))


if __name__ == "__main__":
    main()

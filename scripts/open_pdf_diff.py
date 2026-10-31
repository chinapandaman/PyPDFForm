# -*- coding: utf-8 -*-
"""
Generates and opens a visual diff of two PDF files.

This script takes a "before" PDF file path, an "after" PDF file path, and an
output directory. It converts both PDFs to PNG images in the output
directory, creates a visual diff image, and prints the pixel difference count.

Finally, it attempts to open the before, after, and diff images in a
web browser or the default image viewer, and prints their accessible URLs
for web-based environments.

Usage:
    python scripts/open_pdf_diff.py <before_pdf> <after_pdf> <output_dir>
"""

import os
import subprocess
import sys
import webbrowser

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    before_path = os.path.abspath(sys.argv[1])
    after_path = os.path.abspath(sys.argv[2])
    output_dir = os.path.abspath(sys.argv[3])

    before = os.path.join(output_dir, "before.png")
    after = os.path.join(output_dir, "after.png")
    pdf_diff = os.path.join(output_dir, "pdf_diff.png")

    subprocess.run(
        ["pdftoppm", "-png", before_path, os.path.join(output_dir, "before")]
    )
    subprocess.run(["pdftoppm", "-png", after_path, os.path.join(output_dir, "after")])

    magick = ["convert"]
    if sys.platform == "darwin":
        magick = ["magick"]

    subprocess.run(
        magick + [os.path.join(output_dir, "before-*.png"), "-append", before]
    )
    subprocess.run(magick + [os.path.join(output_dir, "after-*.png"), "-append", after])

    pdf_diff_count = subprocess.run(
        ["compare", "-metric", "AE", before, after, pdf_diff], capture_output=True
    )

    base_url = "./"
    if (
        os.environ.get("CODESPACES") == "true"
        or os.environ.get("PYPDFFORM_ENV") == "container"
    ):
        base_url = "https://{}-8000.app.github.dev/".format(
            os.environ.get("CODESPACE_NAME")
        )
        if os.environ.get("PYPDFFORM_ENV") == "container":
            base_url = "http://localhost:8000/"
    else:
        if sys.platform == "darwin":
            chrome = "Google Chrome"
            if os.environ.get("ACROBAT") == "true":
                acrobat = "Adobe Acrobat"
                subprocess.run(["open", "-a", acrobat, before_path])
                subprocess.run(["open", "-a", acrobat, after_path])
            else:
                subprocess.run(["open", "-a", chrome, before_path])
                subprocess.run(["open", "-a", chrome, after_path])
                subprocess.run(["open", "-a", chrome, pdf_diff])
        else:
            chrome = "/usr/bin/google-chrome %s"
            webbrowser.get(chrome).open(before_path)
            webbrowser.get(chrome).open(after_path)
            webbrowser.get(chrome).open(pdf_diff)

    print("Before:", base_url + os.path.relpath(before_path, project_root))
    print("After:", base_url + os.path.relpath(after_path, project_root))
    print("Diff:", base_url + os.path.relpath(pdf_diff, project_root))
    print("Diff Count:", pdf_diff_count.stderr or 0)

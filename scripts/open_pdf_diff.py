# -*- coding: utf-8 -*-
"""Opens a diff of a PDF between changes."""

import os
import subprocess
import sys
import webbrowser

if __name__ == "__main__":
    project_root = "PyPDFForm"
    if os.environ.get("PYPDFFORM_ENV") == "container":
        project_root = project_root.lower()
    before_path = sys.argv[1]
    file_name = "_".join(before_path.split("/"))
    after_path = os.path.join(os.path.dirname(__file__), "..", "temp", file_name)

    before = os.path.join(os.path.dirname(__file__), "..", "temp", "before.png")
    after = os.path.join(os.path.dirname(__file__), "..", "temp", "after.png")
    pdf_diff = os.path.join(os.path.dirname(__file__), "..", "temp", "pdf_diff.png")

    subprocess.run(["pdftoppm", "-png", before_path, "temp/before"])
    subprocess.run(["pdftoppm", "-png", after_path, "temp/after"])

    subprocess.run(["magick", "temp/before-*.png", "-append", before])
    subprocess.run(["magick", "temp/after-*.png", "-append", after])

    subprocess.run(["compare", "-metric", "AE", before, after, pdf_diff])

    if (
        os.environ.get("CODESPACES") == "true"
        or os.environ.get("PYPDFFORM_ENV") == "container"
    ):
        base_url = "https://{}-8000.app.github.dev/".format(
            os.environ.get("CODESPACE_NAME")
        )
        if os.environ.get("PYPDFFORM_ENV") == "container":
            base_url = "http://localhost:8000/"
        print("Before:", base_url + before_path.split(f"{project_root}/")[1])
        print("After:", base_url + after_path.split(f"{project_root}/./scripts/../")[1])
    else:
        if sys.platform == "darwin":
            subprocess.run(["open", "-a", "Adobe Acrobat", before_path])
            subprocess.run(["open", "-a", "Adobe Acrobat", after_path])
            subprocess.run(["open", "-a", "Google Chrome", pdf_diff])
        else:
            webbrowser.get("/usr/bin/google-chrome %s").open(before_path)
            webbrowser.get("/usr/bin/google-chrome %s").open(after_path)
            webbrowser.get("/usr/bin/google-chrome %s").open(pdf_diff)

        print("Checking", before_path)

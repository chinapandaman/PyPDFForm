# -*- coding: utf-8 -*-
"""Opens a diff of a PDF between changes."""

import os
import sys
import webbrowser

if __name__ == "__main__":
    project_root = "PyPDFForm"
    if os.environ.get("PYPDFFORM_ENV") == "container":
        project_root = project_root.lower()
    before_path = sys.argv[1]
    file_name = "_".join(before_path.split("/"))
    after_path = os.path.join(os.path.dirname(__file__), "..", "temp", file_name)

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
        webbrowser.get("/usr/bin/google-chrome %s").open(before_path)
        webbrowser.get("/usr/bin/google-chrome %s").open(after_path)

        print("Checking", before_path)

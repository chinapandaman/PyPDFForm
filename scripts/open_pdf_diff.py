# -*- coding: utf-8 -*-
"""Opens a diff of a PDF between changes."""

import os
import sys
import webbrowser

if __name__ == "__main__":
    before_path = sys.argv[1]
    file_name = os.path.basename(os.path.abspath(before_path))
    after_path = os.path.join(os.path.dirname(__file__), "..", "temp", file_name)

    if os.environ.get("CODESPACES") == "true":
        base_url = "https://{}-8000.app.github.dev/".format(
            os.environ.get("CODESPACE_NAME")
        )
        print("Before:", base_url + before_path.split("PyPDFForm/")[1])
        print("After:", base_url + after_path.split("PyPDFForm/./scripts/../")[1])
    else:
        webbrowser.get("/usr/bin/google-chrome %s").open(before_path)
        webbrowser.get("/usr/bin/google-chrome %s").open(after_path)

        print("Checking", before_path)

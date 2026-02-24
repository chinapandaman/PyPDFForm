# -*- coding: utf-8 -*-
"""
Creates a new GitHub release for the current version.

This script reads the version from PyPDFForm/__init__.py and compares it
to the latest version fetched from the repository, provided as an argument.
If the current version is newer, it proceeds to create a new GitHub release.
The release is tagged with the new version number, and release notes are
generated automatically by GitHub.

Requires the GITHUB_TOKEN environment variable for authentication.

Usage:
    python scripts/create_release.py <latest_deployed_version>
"""

import os
import re
import sys

import requests

if __name__ == "__main__":
    with open("PyPDFForm/__init__.py", encoding="utf8") as f:
        version = re.search(r'__version__ = "(.*?)"', f.read())
        if version:
            version = version.group(1)

    latest_version = sys.argv[1].replace("(", "").replace(")", "")
    print(f"Latest deployed version: {latest_version}.")
    if latest_version == f"v{version}":
        sys.exit(f"{latest_version} is already deployed.")

    print(f"Bumping to: v{version}")
    token = os.environ.get("GITHUB_TOKEN")

    url = "https://api.github.com/repos/chinapandaman/PyPDFForm/releases"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }
    body = {
        "tag_name": f"v{version}",
        "name": f"v{version}",
        "generate_release_notes": True,
    }

    response = requests.post(
        url=url,
        headers=headers,
        json=body,
    )

    if response.status_code == 201:
        print(f"Successfully deployed v{version}.")
    else:
        print(f"Failed deploying v{version}. Status code: {response.status_code}.")

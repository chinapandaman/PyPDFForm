# -*- coding: utf-8 -*-
"""
Closes stale GitHub issues.

This script fetches all open issues from the project's GitHub repository.
It identifies issues where the last comment is older than 90 days and
the issue is not marked with the "help wanted" label. For each stale issue,
it posts a comment explaining that the issue is being closed due to
inactivity and then closes the issue.

Requires the GITHUB_TOKEN environment variable to be set for API authentication.
"""

import json
import os
from datetime import UTC, datetime, timedelta

import requests
from dateutil.parser import parse

if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }

    issues = json.loads(
        requests.get(
            "https://api.github.com/repos/chinapandaman/PyPDFForm/issues",
            headers=headers,
        ).content
    )

    to_close = []
    for each in issues:
        labels = [label["name"] for label in each["labels"]]
        comments = json.loads(
            requests.get(each["comments_url"], headers=headers).content
        )
        if (
            comments
            and (
                datetime.now(tz=UTC)
                - parse(comments[-1]["updated_at"]).replace(tzinfo=UTC)
                > timedelta(days=90)
            )
            and "help wanted" not in labels
        ):
            to_close.append(each["url"])

    for each in to_close:
        requests.post(
            f"{each}/comments",
            headers=headers,
            json={"body": "Closing due to inactivity."},
        )
        requests.patch(each, headers=headers, json={"state": "closed"})

# -*- coding: utf-8 -*-
"""
Closes issues that have been waiting for their reporter for too long.

A maintainer adds the "awaiting response" label to an issue when they need
more information from the reporter. This script closes an open issue only if
that label was last added at least 30 days ago and nobody other than a
maintainer (the repository owner, members, and collaborators) has commented
since. Issues without the label and pull requests are never closed. Each
closed issue gets a comment saying that it was not resolved and is closed as
"not planned", so inactivity is never recorded as a resolution.

By default, the script only prints what it would do. Pass --apply to comment
on and close the issues, which requires the GITHUB_TOKEN environment
variable. Every issue is checked before anything is changed. Any failure,
including an unexpected API response, a request error, or a timeout, stops
the script with exit status 1.

Usage:
    python scripts/close_staled_issues.py [--apply]
"""

import argparse
import os
import sys
from datetime import UTC, datetime, timedelta

import requests

REPOSITORY = "chinapandaman/PyPDFForm"
API_URL = f"https://api.github.com/repos/{REPOSITORY}"
LABEL = "awaiting response"
WAITING_PERIOD = timedelta(days=30)
REQUEST_TIMEOUT = 30
PAGE_SIZE = 100
MAX_PAGES = 100
MAINTAINERS = frozenset({"OWNER", "MEMBER", "COLLABORATOR"})
MARKER = "<!-- close_staled_issues -->"
CLOSING_COMMENT = (
    f"Closing because this issue has been labeled `{LABEL}` for "
    f"{WAITING_PERIOD.days} days without a reply. This does not mean it has "
    "been resolved. If you can provide the requested information, comment "
    f"here and a maintainer will reopen it.\n\n{MARKER}"
)


class ScriptError(Exception):
    """A failure that stops the script with exit status 1."""


def github(session, method, url, payload=None, params=None):
    """Sends a GitHub API request, raising ScriptError if it cannot complete."""
    try:
        return session.request(
            method=method,
            url=url,
            json=payload,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        message = f"{method} {url} failed: {exc}."
        if method != "GET":
            message += " It may still have taken effect."
        raise ScriptError(message) from exc


def json_body(response, kind, action):
    """Returns the response's JSON if it is of the given kind."""
    try:
        data = response.json()
    except ValueError:
        data = None
    if not isinstance(data, kind):
        message = f"Failed to {action}: the response is not a JSON {kind.__name__}."
        raise ScriptError(message)
    return data


def check_status(response, expected, action):
    """Raises ScriptError unless the response has the expected status code."""
    if response.status_code != expected:
        message = (
            f"Failed to {action}. Status code: {response.status_code}. {response.text}"
        )
        raise ScriptError(message)


def get_all(session, url, params, action):
    """Returns the items from every page of a paginated GitHub list endpoint."""
    items = []
    for _ in range(MAX_PAGES):
        response = github(session, "GET", url, params=params)
        check_status(response, 200, action)
        items.extend(json_body(response, list, action))

        url = response.links.get("next", {}).get("url")
        if not url:
            return items
        # The next page's URL already holds the query parameters.
        params = None

    message = f"Failed to {action}: more than {MAX_PAGES} pages."
    raise ScriptError(message)


def text(record, key, what):
    """Returns record[key] if it is a string."""
    value = record.get(key) if isinstance(record, dict) else None
    if not isinstance(value, str):
        message = f"Unexpected API data: {what} has no {key!r} string."
        raise ScriptError(message)
    return value


def timestamp(record, what):
    """Returns the created_at time of an API record."""
    value = text(record, "created_at", what)
    try:
        result = datetime.fromisoformat(value)
    except ValueError:
        result = None
    if result is None or result.tzinfo is None:
        message = f"Unexpected API data: {what} has an invalid time {value!r}."
        raise ScriptError(message)
    return result


def check_issue(record):
    """Raises ScriptError unless an issue list record has the fields used here."""
    number = record.get("number") if isinstance(record, dict) else None
    if not isinstance(number, int) or isinstance(number, bool):
        message = "Unexpected API data: an issue has no number."
        raise ScriptError(message)

    what = f"issue #{number}"
    text(record, "html_url", what)
    labels = record.get("labels")
    if not isinstance(labels, list):
        message = f"Unexpected API data: {what} has no label list."
        raise ScriptError(message)
    for label in labels:
        text(label, "name", f"a label of {what}")


def is_label(name):
    """Returns whether a label name is the awaiting response label."""
    return name.casefold() == LABEL.casefold()


def review(session, issue, now):
    """Returns whether to close an issue, why, and if it has the closing comment."""
    number = issue["number"]
    if "pull_request" in issue:
        return False, "pull request", False
    if not any(is_label(label["name"]) for label in issue["labels"]):
        return False, f"not labeled {LABEL!r}", False

    events = get_all(
        session,
        f"{API_URL}/issues/{number}/timeline",
        {"per_page": PAGE_SIZE},
        f"list the timeline of issue #{number}",
    )

    labeled_at = None
    for event in events:
        if text(event, "event", f"an event of issue #{number}") != "labeled":
            continue
        what = f"a labeled event of issue #{number}"
        if is_label(text(event.get("label"), "name", what)):
            created = timestamp(event, what)
            labeled_at = created if labeled_at is None else max(labeled_at, created)
    if labeled_at is None:
        return False, f"no record of when {LABEL!r} was added", False

    reply = None
    commented = False
    for event in events:
        if event["event"] != "commented":
            continue
        what = f"a comment on issue #{number}"
        created = timestamp(event, what)
        if created < labeled_at:
            continue
        if text(event, "author_association", what) not in MAINTAINERS:
            user = event.get("user")
            login = user.get("login") if isinstance(user, dict) else None
            if reply is None or created > reply[0]:
                reply = (created, login or "unknown user")
        elif MARKER in (event.get("body") or ""):
            commented = True

    if reply is not None:
        return False, f"@{reply[1]} replied on {reply[0].date()}", False
    due = labeled_at + WAITING_PERIOD
    if due > now:
        return False, f"labeled {labeled_at.date()}, can close from {due.date()}", False
    return (
        True,
        f"labeled {labeled_at.date()}, no non-maintainer reply since",
        commented,
    )


def close(session, number, commented):
    """Posts the closing comment unless it exists, then closes the issue."""
    url = f"{API_URL}/issues/{number}"
    if not commented:
        response = github(session, "POST", f"{url}/comments", {"body": CLOSING_COMMENT})
        action = f"comment on issue #{number}"
        check_status(response, 201, action)
        json_body(response, dict, action)

    response = github(
        session, "PATCH", url, {"state": "closed", "state_reason": "not_planned"}
    )
    action = f"close issue #{number}"
    check_status(response, 200, action)
    data = json_body(response, dict, action)
    if data.get("state") != "closed" or data.get("state_reason") != "not_planned":
        message = f"GitHub did not report issue #{number} as closed as not planned."
        raise ScriptError(message)


def plan(session, now):
    """Prints and returns the issues to close and if each has the comment."""
    records = get_all(
        session,
        f"{API_URL}/issues",
        {"state": "open", "labels": LABEL, "per_page": PAGE_SIZE},
        f"list open issues labeled {LABEL!r}",
    )
    for record in records:
        check_issue(record)
    if not records:
        print("None found.")

    to_close = []
    for record in records:
        closable, reason, commented = review(session, record, now)
        print(
            f"#{record['number']} {'close' if closable else 'skip'}: "
            f"{reason}. {record['html_url']}"
        )
        if closable:
            to_close.append((record["number"], commented))
    return to_close


def run(apply):
    """Prints what to do with each labeled issue and, if apply, does it."""
    token = os.environ.get("GITHUB_TOKEN")
    if apply and not token:
        message = "GITHUB_TOKEN is not set; it is required with --apply."
        raise ScriptError(message)

    session = requests.Session()
    session.headers["Accept"] = "application/vnd.github+json"
    if token:
        session.headers["Authorization"] = f"Bearer {token}"

    now = datetime.now(tz=UTC)
    print(
        f"Open issues in {REPOSITORY} labeled {LABEL!r}, closed after "
        f"{WAITING_PERIOD.days} days without a reply, as of "
        f"{now.isoformat(timespec='seconds')}:"
    )
    try:
        to_close = plan(session, now)
    except ScriptError as exc:
        message = f"{exc} Nothing was changed."
        raise ScriptError(message) from exc

    if not apply:
        print(
            f"Preview only; nothing was changed. Pass --apply to close "
            f"{len(to_close)} issue(s)."
        )
        return

    for done, (number, commented) in enumerate(to_close):
        try:
            close(session, number, commented)
        except ScriptError as exc:
            message = f"{exc} Stopped after closing {done} issue(s)."
            raise ScriptError(message) from exc
        print(f"Closed #{number} as not planned.")
    print(f"Closed {len(to_close)} issue(s).")


def main():
    """Runs the script, exiting with status 1 on any failure."""
    parser = argparse.ArgumentParser(
        description=(
            f"Close issues labeled {LABEL!r} after {WAITING_PERIOD.days} days "
            "without a reply. Only previews by default."
        )
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="comment on and close the issues instead of only listing them",
    )
    args = parser.parse_args()

    try:
        run(args.apply)
    except ScriptError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

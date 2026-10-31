# -*- coding: utf-8 -*-
"""
Creates a new GitHub release for the version at a target commit.

This script reads the version from PyPDFForm/__init__.py at the target commit,
which must be a full commit SHA reachable from origin/master. If that version
is already released with its tag on GitHub pointing at the target commit,
nothing is created and the script succeeds, so reruns are safe. A tag that
points at any other commit is rejected.

Otherwise, the version must be the next patch, minor, or major version after
the highest other vX.Y.Z tag. The script creates the tag at the target commit
on GitHub if it does not exist yet, then creates the release for that tag with
release notes generated automatically by GitHub. Any failure, including an
unexpected API response, a request error, or a timeout, exits with status 1.

Requires the GITHUB_TOKEN environment variable for authentication.

Usage:
    python scripts/create_release.py <target_sha>
"""

import os
import re
import subprocess
import sys

import requests

API_URL = "https://api.github.com/repos/chinapandaman/PyPDFForm"
RELEASES_PAGE = "https://github.com/chinapandaman/PyPDFForm/releases"
DEFAULT_BRANCH = "origin/master"
REQUEST_TIMEOUT = 30
MAX_TAG_DEPTH = 5
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
VERSION_PATTERN = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")


def git(*args):
    """Returns the exit status and stripped stdout of a git command."""
    try:
        result = subprocess.run(["git", *args], capture_output=True, text=True)
    except OSError as exc:
        message = f"Unable to run git: {exc}"
        raise RuntimeError(message) from exc
    return result.returncode, result.stdout.strip()


def github(token, method, path, payload=None):
    """Sends a GitHub API request, raising RuntimeError if it cannot complete."""
    try:
        return requests.request(
            method=method,
            url=f"{API_URL}/{path}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
            },
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        message = f"{method} {path} failed: {exc}."
        if method != "GET":
            message += (
                f" It may still have taken effect; check {RELEASES_PAGE}, then rerun."
            )
        raise RuntimeError(message) from exc


def json_object(response):
    """Returns the JSON object in a response, or an empty dict otherwise."""
    try:
        data = response.json()
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def unexpected(response, action):
    """Returns a RuntimeError describing an unexpected API response."""
    message = (
        f"Failed to {action}. Status code: {response.status_code}. {response.text}"
    )
    return RuntimeError(message)


def parse_version(text):
    """Returns (major, minor, patch) for a strict X.Y.Z version, otherwise None."""
    match = VERSION_PATTERN.fullmatch(text)
    return tuple(int(each) for each in match.groups()) if match else None


def format_tag(version):
    """Returns the vX.Y.Z tag name for a parsed version."""
    return "v" + ".".join(str(each) for each in version)


def check_target(sha):
    """Raises RuntimeError unless sha is a full commit SHA on origin/master."""
    if not SHA_PATTERN.fullmatch(sha):
        message = f"Target must be a full 40-character commit SHA, got {sha!r}."
        raise RuntimeError(message)

    status, _ = git("cat-file", "-e", f"{sha}^{{commit}}")
    if status != 0:
        message = f"Target {sha} is not a commit in this repository."
        raise RuntimeError(message)

    status, _ = git("merge-base", "--is-ancestor", sha, DEFAULT_BRANCH)
    if status == 1:
        message = f"Target {sha} is not on {DEFAULT_BRANCH}."
        raise RuntimeError(message)
    if status != 0:
        message = f"Unable to check whether {sha} is on {DEFAULT_BRANCH}."
        raise RuntimeError(message)


def read_version(sha):
    """Returns the parsed __version__ of PyPDFForm/__init__.py at sha."""
    status, content = git("show", f"{sha}:PyPDFForm/__init__.py")
    match = re.search(r'__version__ = "(.*?)"', content)
    if status != 0 or not match:
        message = f"Unable to read __version__ from PyPDFForm/__init__.py at {sha}."
        raise RuntimeError(message)

    version = parse_version(match.group(1))
    if version is None:
        message = f"Version {match.group(1)!r} at {sha} is not a valid X.Y.Z version."
        raise RuntimeError(message)
    return version


def latest_tag(exclude):
    """Returns the highest vX.Y.Z tag other than exclude and its parsed version."""
    status, output = git("tag", "--list", "v*")
    if status != 0:
        message = "Unable to list tags."
        raise RuntimeError(message)

    tags = {}
    for each in output.splitlines():
        version = parse_version(each[1:])
        if version is not None and each != exclude:
            tags[version] = each
    if not tags:
        message = "No vX.Y.Z tags found to compare against."
        raise RuntimeError(message)

    version = max(tags)
    return tags[version], version


def next_versions(version):
    """Returns the next patch, minor, and major versions after version."""
    major, minor, patch = version
    return [
        (major, minor, patch + 1),
        (major, minor + 1, 0),
        (major + 1, 0, 0),
    ]


def remote_tag_commit(token, tag):
    """Returns the commit SHA that tag points at on GitHub, or None if it is absent."""
    response = github(token, "GET", f"git/ref/tags/{tag}")
    if response.status_code == 404:
        return None
    if response.status_code != 200:
        raise unexpected(response, f"look up tag {tag}")

    target = json_object(response).get("object")
    for _ in range(MAX_TAG_DEPTH):
        if not isinstance(target, dict):
            break
        sha = target.get("sha")
        if not isinstance(sha, str) or not SHA_PATTERN.fullmatch(sha):
            break
        if target.get("type") == "commit":
            return sha
        if target.get("type") != "tag":
            break

        # Annotated tags point at a tag object; follow it to the commit.
        response = github(token, "GET", f"git/tags/{sha}")
        if response.status_code != 200:
            raise unexpected(response, f"look up tag {tag}")
        target = json_object(response).get("object")

    message = f"Tag {tag} on GitHub does not resolve to a commit."
    raise RuntimeError(message)


def release_exists(token, tag):
    """Returns whether GitHub has a release for tag."""
    response = github(token, "GET", f"releases/tags/{tag}")
    if response.status_code == 404:
        return False
    if response.status_code != 200:
        raise unexpected(response, f"look up the release for {tag}")
    return True


def create_tag(token, tag, sha):
    """Creates tag at sha on GitHub, failing if the tag already exists."""
    response = github(
        token, "POST", "git/refs", {"ref": f"refs/tags/{tag}", "sha": sha}
    )
    if response.status_code != 201:
        raise unexpected(response, f"create tag {tag} at {sha}")


def create_release(token, tag, sha):
    """Creates the release for tag, which must already point at sha on GitHub."""
    # GitHub ignores target_commitish while the tag exists; it only applies
    # if the tag was deleted after it was checked.
    body = {
        "tag_name": tag,
        "target_commitish": sha,
        "name": tag,
        "generate_release_notes": True,
    }
    response = github(token, "POST", "releases", body)
    if response.status_code != 201:
        error = unexpected(response, f"create release {tag}")
        message = f"{error} Tag {tag} points at {sha}; rerun to create the release."
        raise RuntimeError(message)

    if json_object(response).get("tag_name") != tag:
        message = (
            f"GitHub reported a new release, but not for {tag}; check {RELEASES_PAGE}."
        )
        raise RuntimeError(message)


def release(sha):
    """Releases the version at sha unless it is already released there."""
    check_target(sha)
    version = read_version(sha)
    tag = format_tag(version)
    print(f"Target: {tag} at {sha}.")

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        message = "GITHUB_TOKEN is not set."
        raise RuntimeError(message)

    tagged = remote_tag_commit(token, tag)
    if tagged is not None and tagged != sha:
        message = (
            f"{tag} already points at {tagged}, not {sha}; bump the version first."
        )
        raise RuntimeError(message)
    if tagged == sha and release_exists(token, tag):
        print(f"{tag} is already released at {sha}; nothing created.")
        return

    latest, latest_version = latest_tag(tag)
    print(f"Latest other tag: {latest}.")
    allowed = next_versions(latest_version)
    if version not in allowed:
        message = (
            f"{tag} must be the next version after {latest}: "
            f"{', '.join(format_tag(each) for each in allowed)}."
        )
        raise RuntimeError(message)

    if tagged is None:
        create_tag(token, tag, sha)
        print(f"Created tag {tag} at {sha}.")
    create_release(token, tag, sha)
    print(f"Successfully created {tag} at {sha}.")


def main():
    """Creates the release, exiting with status 1 on any failure."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/create_release.py <target_sha>", file=sys.stderr)
        sys.exit(1)

    try:
        release(sys.argv[1])
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

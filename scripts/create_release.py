# -*- coding: utf-8 -*-
"""
Creates a new GitHub release for the version at a target commit.

This script reads the version from PyPDFForm/__init__.py at the target commit,
which must be a full commit SHA reachable from origin/master. The version must
be the next patch, minor, or major version after the highest vX.Y.Z tag. The
release is created at exactly that commit and tagged with the new version
number, and release notes are generated automatically by GitHub.

If the version's tag already points at the target commit, nothing is created
and the script succeeds, so reruns are safe. Any other failure, including an
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

RELEASES_URL = "https://api.github.com/repos/chinapandaman/PyPDFForm/releases"
RELEASES_PAGE = "https://github.com/chinapandaman/PyPDFForm/releases"
DEFAULT_BRANCH = "origin/master"
REQUEST_TIMEOUT = 30
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


def latest_tag():
    """Returns the highest vX.Y.Z tag and its parsed version."""
    status, output = git("tag", "--list", "v*")
    if status != 0:
        message = "Unable to list tags."
        raise RuntimeError(message)

    tags = {}
    for each in output.splitlines():
        version = parse_version(each[1:])
        if version is not None:
            tags[version] = each
    if not tags:
        message = "No vX.Y.Z tags found to compare against."
        raise RuntimeError(message)

    version = max(tags)
    return tags[version], version


def tag_commit(tag):
    """Returns the commit SHA that tag points at."""
    status, sha = git("rev-parse", f"{tag}^{{commit}}")
    if status != 0:
        message = f"Unable to resolve the commit for {tag}."
        raise RuntimeError(message)
    return sha


def next_versions(version):
    """Returns the next patch, minor, and major versions after version."""
    major, minor, patch = version
    return [
        (major, minor, patch + 1),
        (major, minor + 1, 0),
        (major + 1, 0, 0),
    ]


def create_release(tag, sha):
    """Creates the release at sha, raising RuntimeError unless GitHub confirms it."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        message = "GITHUB_TOKEN is not set."
        raise RuntimeError(message)

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }
    body = {
        "tag_name": tag,
        "target_commitish": sha,
        "name": tag,
        "generate_release_notes": True,
    }

    try:
        response = requests.post(
            url=RELEASES_URL,
            headers=headers,
            json=body,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        message = (
            f"Request to create {tag} failed: {exc}. The release may still have "
            f"been created; check {RELEASES_PAGE}, then rerun."
        )
        raise RuntimeError(message) from exc

    if response.status_code != 201:
        message = (
            f"Failed creating {tag}. Status code: {response.status_code}. "
            f"{response.text}"
        )
        raise RuntimeError(message)

    try:
        data = response.json()
    except ValueError:
        data = None
    if (
        not isinstance(data, dict)
        or data.get("tag_name") != tag
        or data.get("target_commitish") != sha
    ):
        message = (
            f"GitHub reported a new release, but not {tag} at {sha}; "
            f"check {RELEASES_PAGE}."
        )
        raise RuntimeError(message)


def release(sha):
    """Releases the version at sha unless its tag already points at sha."""
    check_target(sha)
    version = read_version(sha)
    latest, latest_version = latest_tag()
    tag = format_tag(version)
    print(f"Latest tag: {latest}. Target: {tag} at {sha}.")

    if version == latest_version:
        tagged = tag_commit(latest)
        if tagged == sha:
            print(f"{tag} is already released at {sha}; nothing created.")
            return
        message = f"{tag} is already released at {tagged}; bump the version first."
        raise RuntimeError(message)

    allowed = next_versions(latest_version)
    if version not in allowed:
        message = (
            f"{tag} must be the next version after {latest}: "
            f"{', '.join(format_tag(each) for each in allowed)}."
        )
        raise RuntimeError(message)

    create_release(tag, sha)
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

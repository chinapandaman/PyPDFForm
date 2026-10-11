# -*- coding: utf-8 -*-
"""
This script extracts Python code snippets from the documentation files (specifically those listed
under the 'User Guide' in mkdocs.yml) and runs pyright on them to ensure type correctness.

It performs the following steps:
1. Creates a temporary 'ci_artifacts' directory.
2. Identifies 'User Guide' documentation files from mkdocs.yml.
3. Extracts all python code blocks from these files and saves them as standalone .py files.
4. Executes pyright on these generated files.
5. Maps any reported diagnostics back to the original documentation files and line numbers.
6. Cleans up the temporary artifacts.
7. Exits with a non-zero status if diagnostics or checker failures are detected.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import textwrap

import yaml


def setup_artifact_dir(artifact_dir):
    """Creates the artifact directory and a pyrightconfig.json with repo imports."""
    if not os.path.exists(artifact_dir):
        os.makedirs(artifact_dir)

    with open(os.path.join(artifact_dir, "pyrightconfig.json"), "w") as f:
        json.dump({"extraPaths": [".."]}, f)


def get_user_guide_docs(mkdocs_path):
    """Extracts User Guide document paths from mkdocs.yml after sanitizing custom tags."""
    with open(mkdocs_path, "r") as f:
        content = f.read()

    content = re.sub(r"!!python/name:[\w\.]+", "null", content)
    config = yaml.safe_load(content)

    nav = config.get("nav", [])
    for item in nav:
        if isinstance(item, dict) and "User Guide" in item:
            return item["User Guide"]
    return []


def _extract_snippets_from_file(
    lines, doc_file, doc_path, artifact_dir, snippet_map, snippet_idx
):
    """Extracts Python code blocks from one doc file and records source locations."""
    in_code_block = False
    code_lines = []
    start_line = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```python"):
            in_code_block = True
            start_line = i + 1
            code_lines = []
        elif stripped.startswith("```") and in_code_block:
            in_code_block = False
            if not code_lines:
                continue

            safe_doc_name = doc_file.replace("/", "_").replace(".", "_")
            snippet_filename = f"{safe_doc_name}_{snippet_idx}.py"
            snippet_path = os.path.join(artifact_dir, snippet_filename)

            dedented_code = textwrap.dedent("".join(code_lines))
            with open(snippet_path, "w") as sf:
                sf.write(dedented_code)

            snippet_map[snippet_filename] = (doc_path, start_line)
            snippet_idx += 1
        elif in_code_block:
            code_lines.append(line)

    return snippet_idx


def extract_snippets(user_guide_docs, artifact_dir):
    """Extracts Python snippets from existing User Guide docs and saves them to files."""
    snippet_map = {}
    snippet_idx = 0

    for doc_file in user_guide_docs:
        if not isinstance(doc_file, str):
            continue

        doc_path = os.path.join("docs", doc_file)
        if not os.path.exists(doc_path):
            continue

        with open(doc_path, "r") as f:
            lines = f.readlines()

        snippet_idx = _extract_snippets_from_file(
            lines, doc_file, doc_path, artifact_dir, snippet_map, snippet_idx
        )

    return snippet_map


def _get_diagnostics(data):
    """Validates the Pyright JSON fields needed to report diagnostics."""
    if not isinstance(data, dict) or not isinstance(
        data.get("generalDiagnostics"), list
    ):
        message = "expected a JSON object with a generalDiagnostics list"
        raise TypeError(message)

    diagnostics = data["generalDiagnostics"]
    for diag in diagnostics:
        location = diag.get("range") if isinstance(diag, dict) else None
        start = location.get("start") if isinstance(location, dict) else None
        line = start.get("line") if isinstance(start, dict) else None
        if (
            not isinstance(diag, dict)
            or not isinstance(diag.get("file"), str)
            or not diag["file"].strip()
            or not isinstance(diag.get("message"), str)
            or diag.get("severity") not in ("error", "warning", "information")
            or type(line) is not int
            or line < 0
        ):
            message = "expected diagnostic file, message, severity, and nonnegative integer start line"
            raise ValueError(message)

    return diagnostics


def run_pyright(artifact_dir):
    """Returns validated diagnostics or raises RuntimeError for checker failures."""
    cmd = [
        "pyright",
        "--outputjson",
        "--project",
        os.path.join(artifact_dir, "pyrightconfig.json"),
        artifact_dir,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except OSError as exc:
        message = f"Unable to run Pyright: {exc}"
        raise RuntimeError(message) from exc

    details = f"exit status {result.returncode}"
    if result.stderr.strip():
        details += f"\n{result.stderr.strip()}"

    try:
        diagnostics = _get_diagnostics(json.loads(result.stdout))
    except (TypeError, ValueError) as exc:
        message = f"Invalid Pyright JSON: {exc} ({details})"
        raise RuntimeError(message) from exc

    # Pyright uses status 1 for type errors; keep those diagnostics for source mapping.
    has_type_errors = any(diag["severity"] == "error" for diag in diagnostics)
    if result.returncode != 0 and not (result.returncode == 1 and has_type_errors):
        message = f"Pyright failed with {details}"
        raise RuntimeError(message)

    return diagnostics


def map_diagnostics(diagnostics, snippet_map):
    """Maps pyright diagnostics back to original documentation files and lines."""
    errors_by_location = {}

    for diag in diagnostics:
        file_path = diag.get("file")
        filename = os.path.basename(file_path)
        error_line_in_snippet = diag["range"]["start"]["line"]

        if filename in snippet_map:
            original_doc, start_line = snippet_map[filename]
            original_line = start_line + 1 + error_line_in_snippet
        else:
            original_doc = file_path
            original_line = error_line_in_snippet + 1
        msg = diag.get("message", "")

        if original_doc not in errors_by_location:
            errors_by_location[original_doc] = {}
        if original_line not in errors_by_location[original_doc]:
            errors_by_location[original_doc][original_line] = []

        errors_by_location[original_doc][original_line].append(msg)

    return errors_by_location


def report_errors(errors_by_location):
    """Prints consolidated errors and returns True if any errors were found."""
    has_errors = False
    for doc_path in sorted(errors_by_location.keys()):
        for line_num in sorted(errors_by_location[doc_path].keys()):
            has_errors = True
            messages = errors_by_location[doc_path][line_num]
            print(f"{doc_path}:{line_num}")
            for m in messages:
                print(f"  {m}")
    return has_errors


def cleanup(artifact_dir):
    """Removes the artifact directory when it exists."""
    if os.path.exists(artifact_dir):
        shutil.rmtree(artifact_dir)


def main():
    """Checks documentation snippets, failing on diagnostics or checker errors."""
    artifact_dir = "ci_artifacts"
    try:
        setup_artifact_dir(artifact_dir)
        user_guide_docs = get_user_guide_docs("mkdocs.yml")
        snippet_map = extract_snippets(user_guide_docs, artifact_dir)
        diagnostics = run_pyright(artifact_dir)
        errors_by_location = map_diagnostics(diagnostics, snippet_map)
        if report_errors(errors_by_location):
            sys.exit(1)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    finally:
        cleanup(artifact_dir)


if __name__ == "__main__":
    main()
